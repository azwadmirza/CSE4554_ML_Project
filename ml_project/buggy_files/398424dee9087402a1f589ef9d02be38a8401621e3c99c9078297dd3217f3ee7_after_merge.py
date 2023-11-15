    def __call__(self, env, start_response):
        """WSGI `app` method.

        Makes instances of API callable from a WSGI server. May be used to
        host an API or called directly in order to simulate requests when
        testing the API.

        See also PEP 3333.

        Args:
            env (dict): A WSGI environment dictionary
            start_response (callable): A WSGI helper function for setting
                status and headers on a response.

        """

        req = self._request_type(env, options=self.req_options)
        resp = self._response_type()
        resource = None
        middleware_stack = []  # Keep track of executed components
        params = {}

        try:
            # NOTE(kgriffs): Using an inner try..except in order to
            # address the case when err_handler raises HTTPError.

            # NOTE(kgriffs): Coverage is giving false negatives,
            # so disabled on relevant lines. All paths are tested
            # afaict.
            try:
                # NOTE(ealogar): The execution of request middleware should be
                # before routing. This will allow request mw to modify path.
                self._call_req_mw(middleware_stack, req, resp)
                # NOTE(warsaw): Moved this to inside the try except because it
                # is possible when using object-based traversal for
                # _get_responder() to fail.  An example is a case where an
                # object does not have the requested next-hop child resource.
                # In that case, the object being asked to dispatch to its
                # child will raise an HTTP exception signalling the problem,
                # e.g. a 404.
                responder, params, resource = self._get_responder(req)

                self._call_rsrc_mw(middleware_stack, req, resp, resource,
                                   params)

                responder(req, resp, **params)
                self._call_resp_mw(middleware_stack, req, resp, resource)

            except Exception as ex:
                for err_type, err_handler in self._error_handlers:
                    if isinstance(ex, err_type):
                        err_handler(ex, req, resp, params)
                        self._call_after_hooks(req, resp, resource)
                        self._call_resp_mw(middleware_stack, req, resp,
                                           resource)

                        break

                else:
                    # PERF(kgriffs): This will propagate HTTPError to
                    # the handler below. It makes handling HTTPError
                    # less efficient, but that is OK since error cases
                    # don't need to be as fast as the happy path, and
                    # indeed, should perhaps be slower to create
                    # backpressure on clients that are issuing bad
                    # requests.

                    # NOTE(ealogar): This will executed remaining
                    # process_response when no error_handler is given
                    # and for whatever exception. If an HTTPError is raised
                    # remaining process_response will be executed later.
                    self._call_resp_mw(middleware_stack, req, resp, resource)
                    raise

        except HTTPStatus as ex:
            self._compose_status_response(req, resp, ex)
            self._call_after_hooks(req, resp, resource)
            self._call_resp_mw(middleware_stack, req, resp, resource)

        except HTTPError as ex:
            self._compose_error_response(req, resp, ex)
            self._call_after_hooks(req, resp, resource)
            self._call_resp_mw(middleware_stack, req, resp, resource)

        #
        # Set status and headers
        #
        if req.method == 'HEAD' or resp.status in self._BODILESS_STATUS_CODES:
            body = []
        else:
            body, length = self._get_body(resp, env.get('wsgi.file_wrapper'))
            if length is not None:
                resp._headers['content-length'] = str(length)

        # NOTE(kgriffs): Based on wsgiref.validate's interpretation of
        # RFC 2616, as commented in that module's source code. The
        # presence of the Content-Length header is not similarly
        # enforced.
        if resp.status in (status.HTTP_204, status.HTTP_304):
            media_type = None
        else:
            media_type = self._media_type

        headers = resp._wsgi_headers(media_type)

        # Return the response per the WSGI spec
        start_response(resp.status, headers)
        return body