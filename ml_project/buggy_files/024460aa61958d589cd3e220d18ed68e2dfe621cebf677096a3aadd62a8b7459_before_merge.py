    def __call__(self, req):
        """
        The method is invoked on every request and shows the lifecycle of the request received from
        the middleware.

        Although some middleware may use parts of the API spec, it is safe to assume that if you're
        looking for the particular spec property handler, it's most likely a part of this method.

        At the time of writing, the only property being utilized by middleware was `x-log-result`.
        """
        LOG.debug("Received call with WebOb: %s", req)
        endpoint, path_vars = self.match(req)
        LOG.debug("Parsed endpoint: %s", endpoint)
        LOG.debug("Parsed path_vars: %s", path_vars)

        context = copy.copy(getattr(self, 'mock_context', {}))
        cookie_token = None

        # Handle security
        if 'security' in endpoint:
            security = endpoint.get('security')
        else:
            security = self.spec.get('security', [])

        if self.auth and security:
            try:
                security_definitions = self.spec.get('securityDefinitions', {})
                for statement in security:
                    declaration, options = statement.copy().popitem()
                    definition = security_definitions[declaration]

                    if definition['type'] == 'apiKey':
                        if definition['in'] == 'header':
                            token = req.headers.get(definition['name'])
                        elif definition['in'] == 'query':
                            token = req.GET.get(definition['name'])
                        elif definition['in'] == 'cookie':
                            token = req.cookies.get(definition['name'])
                        else:
                            token = None

                        if token:
                            auth_func = op_resolver(definition['x-operationId'])
                            auth_resp = auth_func(token)

                            # Include information on how user authenticated inside the context
                            if 'auth-token' in definition['name'].lower():
                                auth_method = 'authentication token'
                            elif 'api-key' in definition['name'].lower():
                                auth_method = 'API key'

                            context['user'] = User.get_by_name(auth_resp.user)
                            context['auth_info'] = {
                                'method': auth_method,
                                'location': definition['in']
                            }

                            # Also include token expiration time when authenticated via auth token
                            if 'auth-token' in definition['name'].lower():
                                context['auth_info']['token_expire'] = auth_resp.expiry

                            if 'x-set-cookie' in definition:
                                max_age = auth_resp.expiry - date_utils.get_datetime_utc_now()
                                cookie_token = cookies.make_cookie(definition['x-set-cookie'],
                                                                   token,
                                                                   max_age=max_age,
                                                                   httponly=True)

                            break

                if 'user' not in context:
                    raise auth_exc.NoAuthSourceProvidedError('One of Token or API key required.')
            except (auth_exc.NoAuthSourceProvidedError,
                    auth_exc.MultipleAuthSourcesError) as e:
                LOG.error(str(e))
                return abort_unauthorized(str(e))
            except auth_exc.TokenNotProvidedError as e:
                LOG.exception('Token is not provided.')
                return abort_unauthorized(str(e))
            except auth_exc.TokenNotFoundError as e:
                LOG.exception('Token is not found.')
                return abort_unauthorized(str(e))
            except auth_exc.TokenExpiredError as e:
                LOG.exception('Token has expired.')
                return abort_unauthorized(str(e))
            except auth_exc.ApiKeyNotProvidedError as e:
                LOG.exception('API key is not provided.')
                return abort_unauthorized(str(e))
            except auth_exc.ApiKeyNotFoundError as e:
                LOG.exception('API key is not found.')
                return abort_unauthorized(str(e))
            except auth_exc.ApiKeyDisabledError as e:
                LOG.exception('API key is disabled.')
                return abort_unauthorized(str(e))

            if cfg.CONF.rbac.enable:
                user_db = context['user']

                permission_type = endpoint.get('x-permissions', None)
                if permission_type:
                    resolver = resolvers.get_resolver_for_permission_type(permission_type)
                    has_permission = resolver.user_has_permission(user_db, permission_type)

                    if not has_permission:
                        raise rbac_exc.ResourceTypeAccessDeniedError(user_db,
                                                                     permission_type)

        # Collect parameters
        kw = {}
        for param in endpoint.get('parameters', []) + endpoint.get('x-parameters', []):
            name = param['name']
            argument_name = param.get('x-as', None) or name
            source = param['in']
            default = param.get('default', None)

            # Collecting params from different sources
            if source == 'query':
                kw[argument_name] = req.GET.get(name, default)
            elif source == 'path':
                kw[argument_name] = path_vars[name]
            elif source == 'header':
                kw[argument_name] = req.headers.get(name, default)
            elif source == 'formData':
                kw[argument_name] = req.POST.get(name, default)
            elif source == 'environ':
                kw[argument_name] = req.environ.get(name.upper(), default)
            elif source == 'context':
                kw[argument_name] = context.get(name, default)
            elif source == 'request':
                kw[argument_name] = getattr(req, name)
            elif source == 'body':
                content_type = req.headers.get('Content-Type', 'application/json')
                content_type = parse_content_type_header(content_type=content_type)[0]
                schema = param['schema']

                # Note: We also want to perform validation if no body is explicitly provided - in a
                # lot of POST, PUT scenarios, body is mandatory
                if not req.body and content_type == 'application/json':
                    req.body = b'{}'

                try:
                    if content_type == 'application/json':
                        data = req.json
                    elif content_type == 'text/plain':
                        data = req.body
                    elif content_type in ['application/x-www-form-urlencoded',
                                          'multipart/form-data']:
                        data = urlparse.parse_qs(req.body)
                    else:
                        raise ValueError('Unsupported Content-Type: "%s"' % (content_type))
                except Exception as e:
                    detail = 'Failed to parse request body: %s' % str(e)
                    raise exc.HTTPBadRequest(detail=detail)

                # Special case for Python 3
                if six.PY3 and content_type == 'text/plain' and isinstance(data, six.binary_type):
                    # Convert bytes to text type (string / unicode)
                    data = data.decode('utf-8')

                try:
                    CustomValidator(schema, resolver=self.spec_resolver).validate(data)
                except (jsonschema.ValidationError, ValueError) as e:
                    raise exc.HTTPBadRequest(detail=e.message,
                                             comment=traceback.format_exc())

                if content_type == 'text/plain':
                    kw[argument_name] = data
                else:
                    class Body(object):
                        def __init__(self, **entries):
                            self.__dict__.update(entries)

                    ref = schema.get('$ref', None)
                    if ref:
                        with self.spec_resolver.resolving(ref) as resolved:
                            schema = resolved

                    if 'x-api-model' in schema:
                        input_type = schema.get('type', [])
                        Model = op_resolver(schema['x-api-model'])

                        if input_type and not isinstance(input_type, (list, tuple)):
                            input_type = [input_type]

                        # root attribute is not an object, we need to use wrapper attribute to
                        # make it work with **kwarg expansion
                        if input_type and 'array' in input_type:
                            data = {'data': data}

                        instance = self._get_model_instance(model_cls=Model, data=data)

                        # Call validate on the API model - note we should eventually move all
                        # those model schema definitions into openapi.yaml
                        try:
                            instance = instance.validate()
                        except (jsonschema.ValidationError, ValueError) as e:
                            raise exc.HTTPBadRequest(detail=e.message,
                                                     comment=traceback.format_exc())
                    else:
                        LOG.debug('Missing x-api-model definition for %s, using generic Body '
                                  'model.' % (endpoint['operationId']))
                        model = Body
                        instance = self._get_model_instance(model_cls=model, data=data)

                    kw[argument_name] = instance

            # Making sure all required params are present
            required = param.get('required', False)
            if required and kw[argument_name] is None:
                detail = 'Required parameter "%s" is missing' % name
                raise exc.HTTPBadRequest(detail=detail)

            # Validating and casting param types
            param_type = param.get('type', None)
            if kw[argument_name] is not None:
                if param_type == 'boolean':
                    positive = ('true', '1', 'yes', 'y')
                    negative = ('false', '0', 'no', 'n')

                    if str(kw[argument_name]).lower() not in positive + negative:
                        detail = 'Parameter "%s" is not of type boolean' % argument_name
                        raise exc.HTTPBadRequest(detail=detail)

                    kw[argument_name] = str(kw[argument_name]).lower() in positive
                elif param_type == 'integer':
                    regex = r'^-?[0-9]+$'

                    if not re.search(regex, str(kw[argument_name])):
                        detail = 'Parameter "%s" is not of type integer' % argument_name
                        raise exc.HTTPBadRequest(detail=detail)

                    kw[argument_name] = int(kw[argument_name])
                elif param_type == 'number':
                    regex = r'^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$'

                    if not re.search(regex, str(kw[argument_name])):
                        detail = 'Parameter "%s" is not of type float' % argument_name
                        raise exc.HTTPBadRequest(detail=detail)

                    kw[argument_name] = float(kw[argument_name])
                elif param_type == 'array' and param.get('items', {}).get('type', None) == 'string':
                    if kw[argument_name] is None:
                        kw[argument_name] = []
                    elif isinstance(kw[argument_name], (list, tuple)):
                        # argument is already an array
                        pass
                    else:
                        kw[argument_name] = kw[argument_name].split(',')

        # Call the controller
        try:
            func = op_resolver(endpoint['operationId'])
        except Exception as e:
            LOG.exception('Failed to load controller for operation "%s": %s' %
                          (endpoint['operationId'], str(e)))
            raise e

        try:
            resp = func(**kw)
        except Exception as e:
            LOG.exception('Failed to call controller function "%s" for operation "%s": %s' %
                          (func.__name__, endpoint['operationId'], str(e)))
            raise e

        # Handle response
        if resp is None:
            resp = Response()

        if not hasattr(resp, '__call__'):
            resp = Response(json=resp)

        responses = endpoint.get('responses', {})
        response_spec = responses.get(str(resp.status_code), None)
        default_response_spec = responses.get('default', None)

        if not response_spec and default_response_spec:
            LOG.debug('No custom response spec found for endpoint "%s", using a default one' %
                      (endpoint['operationId']))
            response_spec_name = 'default'
        else:
            response_spec_name = str(resp.status_code)

        response_spec = response_spec or default_response_spec

        if response_spec and 'schema' in response_spec:
            LOG.debug('Using response spec "%s" for endpoint %s and status code %s' %
                     (response_spec_name, endpoint['operationId'], resp.status_code))

            try:
                validator = CustomValidator(response_spec['schema'], resolver=self.spec_resolver)
                validator.validate(resp.json)
            except (jsonschema.ValidationError, ValueError):
                LOG.exception('Response validation failed.')
                resp.headers.add('Warning', '199 OpenAPI "Response validation failed"')
        else:
            LOG.debug('No response spec found for endpoint "%s"' % (endpoint['operationId']))

        if cookie_token:
            resp.headerlist.append(('Set-Cookie', cookie_token))

        return resp