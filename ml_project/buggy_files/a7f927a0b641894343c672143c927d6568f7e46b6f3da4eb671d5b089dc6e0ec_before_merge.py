    def traverse(self, path, response=None, validated_hook=None):
        """Traverse the object space

        The REQUEST must already have a PARENTS item with at least one
        object in it.  This is typically the root object.
        """
        request = self
        request_get = request.get
        if response is None:
            response = self.response

        # remember path for later use
        browser_path = path

        # Cleanup the path list
        if path[:1] == '/':
            path = path[1:]
        if path[-1:] == '/':
            path = path[:-1]
        clean = []
        for item in path.split('/'):
            # Make sure that certain things that dont make sense
            # cannot be traversed.
            if item in ('REQUEST', 'aq_self', 'aq_base'):
                return response.notFoundError(path)
            if not item or item == '.':
                continue
            elif item == '..':
                del clean[-1]
            else:
                clean.append(item)
        path = clean

        # How did this request come in? (HTTP GET, PUT, POST, etc.)
        method = request_get('REQUEST_METHOD', 'GET').upper()

        # Probably a browser
        no_acquire_flag = 0
        if method in ('GET', 'POST', 'PURGE') and \
           not is_xmlrpc_response(response):
            # index_html is still the default method, only any object can
            # override it by implementing its own __browser_default__ method
            method = 'index_html'
        elif self.maybe_webdav_client:
            # Probably a WebDAV client.
            no_acquire_flag = 1

        URL = request['URL']
        parents = request['PARENTS']
        object = parents[-1]
        del parents[:]

        self.roles = getRoles(None, None, object, UNSPECIFIED_ROLES)

        # if the top object has a __bobo_traverse__ method, then use it
        # to possibly traverse to an alternate top-level object.
        if hasattr(object, '__bobo_traverse__'):
            try:
                new_object = object.__bobo_traverse__(request)
                if new_object is not None:
                    object = new_object
                    self.roles = getRoles(None, None, object,
                                          UNSPECIFIED_ROLES)
            except Exception:
                pass

        if not path and not method:
            return response.forbiddenError(self['URL'])

        # Traverse the URL to find the object:
        if hasattr(object, '__of__'):
            # Try to bind the top-level object to the request
            # This is how you get 'self.REQUEST'
            object = object.__of__(RequestContainer(REQUEST=request))
        parents.append(object)

        steps = self.steps
        self._steps = _steps = list(map(quote, steps))
        path.reverse()

        request['TraversalRequestNameStack'] = request.path = path
        request['ACTUAL_URL'] = request['URL'] + quote(browser_path)

        # Set the posttraverse for duration of the traversal here
        self._post_traverse = post_traverse = []

        entry_name = ''
        try:
            # We build parents in the wrong order, so we
            # need to make sure we reverse it when we're done.
            while 1:
                bpth = getattr(object, '__before_publishing_traverse__', None)
                if bpth is not None:
                    bpth(object, self)

                path = request.path = request['TraversalRequestNameStack']
                # Check for method:
                if path:
                    entry_name = path.pop()
                else:
                    # If we have reached the end of the path, we look to see
                    # if we can find IBrowserPublisher.browserDefault. If so,
                    # we call it to let the object tell us how to publish it.
                    # BrowserDefault returns the object to be published
                    # (usually self) and a sequence of names to traverse to
                    # find the method to be published.

                    # This is webdav support. The last object in the path
                    # should not be acquired. Instead, a NullResource should
                    # be given if it doesn't exist:
                    if no_acquire_flag and \
                       hasattr(object, 'aq_base') and \
                       not hasattr(object, '__bobo_traverse__'):

                        if (object.__parent__ is not
                                aq_inner(object).__parent__):
                            from webdav.NullResource import NullResource
                            object = NullResource(parents[-2], object.getId(),
                                                  self).__of__(parents[-2])

                    if IBrowserPublisher.providedBy(object):
                        adapter = object
                    else:
                        adapter = queryMultiAdapter((object, self),
                                                    IBrowserPublisher)
                        if adapter is None:
                            # Zope2 doesn't set up its own adapters in a lot
                            # of cases so we will just use a default adapter.
                            adapter = DefaultPublishTraverse(object, self)

                    object, default_path = adapter.browserDefault(self)
                    if default_path:
                        request._hacked_path = 1
                        if len(default_path) > 1:
                            path = list(default_path)
                            method = path.pop()
                            request['TraversalRequestNameStack'] = path
                            continue
                        else:
                            entry_name = default_path[0]
                    elif (method
                          and hasattr(object, method)
                          and entry_name != method
                          and getattr(object, method) is not None):
                        request._hacked_path = 1
                        entry_name = method
                        method = 'index_html'
                    else:
                        if hasattr(object, '__call__'):
                            self.roles = getRoles(
                                object, '__call__',
                                object.__call__, self.roles)
                        if request._hacked_path:
                            i = URL.rfind('/')
                            if i > 0:
                                response.setBase(URL[:i])
                        break
                step = quote(entry_name)
                _steps.append(step)
                request['URL'] = URL = '%s/%s' % (request['URL'], step)

                try:
                    subobject = self.traverseName(object, entry_name)
                    if hasattr(object, '__bobo_traverse__') or \
                       hasattr(object, entry_name):
                        check_name = entry_name
                    else:
                        check_name = None

                    self.roles = getRoles(
                        object, check_name, subobject,
                        self.roles)
                    object = subobject
                # traverseName() might raise ZTK's NotFound
                except (KeyError, AttributeError, ztkNotFound):
                    if response.debug_mode:
                        return response.debugError(
                            "Cannot locate object at: %s" % URL)
                    else:
                        return response.notFoundError(URL)
                except Forbidden as e:
                    if self.response.debug_mode:
                        return response.debugError(e.args)
                    else:
                        return response.forbiddenError(entry_name)

                parents.append(object)

                steps.append(entry_name)
        finally:
            parents.reverse()

        # Note - no_acquire_flag is necessary to support
        # things like DAV.  We have to make sure
        # that the target object is not acquired
        # if the request_method is other than GET
        # or POST. Otherwise, you could never use
        # PUT to add a new object named 'test' if
        # an object 'test' existed above it in the
        # hierarchy -- you'd always get the
        # existing object :(
        if no_acquire_flag and \
           hasattr(parents[1], 'aq_base') and \
           not hasattr(parents[1], '__bobo_traverse__'):
            base = aq_base(parents[1])
            if not hasattr(base, entry_name):
                try:
                    if entry_name not in base:
                        raise AttributeError(entry_name)
                except TypeError:
                    raise AttributeError(entry_name)

        # After traversal post traversal hooks aren't available anymore
        del self._post_traverse

        request['PUBLISHED'] = parents.pop(0)

        # Do authorization checks
        user = groups = None
        i = 0

        if 1:  # Always perform authentication.

            last_parent_index = len(parents)
            if hasattr(object, '__allow_groups__'):
                groups = object.__allow_groups__
                inext = 0
            else:
                inext = None
                for i in range(last_parent_index):
                    if hasattr(parents[i], '__allow_groups__'):
                        groups = parents[i].__allow_groups__
                        inext = i + 1
                        break

            if inext is not None:
                i = inext
                v = getattr(groups, 'validate', old_validation)

                auth = request._auth

                if v is old_validation and self.roles is UNSPECIFIED_ROLES:
                    # No roles, so if we have a named group, get roles from
                    # group keys
                    if hasattr(groups, 'keys'):
                        self.roles = list(groups.keys())
                    else:
                        try:
                            groups = groups()
                        except Exception:
                            pass
                        try:
                            self.roles = list(groups.keys())
                        except Exception:
                            pass

                    if groups is None:
                        # Public group, hack structures to get it to validate
                        self.roles = None
                        auth = ''

                if v is old_validation:
                    user = old_validation(groups, request, auth, self.roles)
                elif self.roles is UNSPECIFIED_ROLES:
                    user = v(request, auth)
                else:
                    user = v(request, auth, self.roles)

                while user is None and i < last_parent_index:
                    parent = parents[i]
                    i = i + 1
                    if hasattr(parent, '__allow_groups__'):
                        groups = parent.__allow_groups__
                    else:
                        continue
                    if hasattr(groups, 'validate'):
                        v = groups.validate
                    else:
                        v = old_validation
                    if v is old_validation:
                        user = old_validation(
                            groups, request, auth, self.roles)
                    elif self.roles is UNSPECIFIED_ROLES:
                        user = v(request, auth)
                    else:
                        user = v(request, auth, self.roles)

            if user is None and self.roles != UNSPECIFIED_ROLES:
                response.unauthorized()

        if user is not None:
            if validated_hook is not None:
                validated_hook(self, user)
            request['AUTHENTICATED_USER'] = user
            request['AUTHENTICATION_PATH'] = '/'.join(steps[:-i])

        # Remove http request method from the URL.
        request['URL'] = URL

        # Run post traversal hooks
        if post_traverse:
            result = exec_callables(post_traverse)
            if result is not None:
                object = result

        return object