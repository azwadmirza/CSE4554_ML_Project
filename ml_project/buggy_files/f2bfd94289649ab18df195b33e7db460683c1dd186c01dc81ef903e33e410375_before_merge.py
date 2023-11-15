    def forward(self, method):
        path = self.path
        if '://' in path:
            path = '/' + path.split('://', 1)[1].split('/', 1)[1]
        proxy_url = '%s%s' % (self.proxy.forward_url, path)
        target_url = self.path
        if '://' not in target_url:
            target_url = '%s%s' % (self.proxy.forward_url, target_url)
        data = self.data_bytes

        forward_headers = CaseInsensitiveDict(self.headers)
        # update original "Host" header (moto s3 relies on this behavior)
        if not forward_headers.get('Host'):
            forward_headers['host'] = urlparse(target_url).netloc
        if 'localhost.atlassian.io' in forward_headers.get('Host'):
            forward_headers['host'] = 'localhost'

        try:
            response = None
            modified_request = None
            # update listener (pre-invocation)
            if self.proxy.update_listener:
                listener_result = self.proxy.update_listener.forward_request(method=method,
                    path=path, data=data, headers=forward_headers)
                if isinstance(listener_result, Response):
                    response = listener_result
                elif isinstance(listener_result, Request):
                    modified_request = listener_result
                    data = modified_request.data
                    forward_headers = modified_request.headers
                elif listener_result is not True:
                    # get status code from response, or use Bad Gateway status code
                    code = listener_result if isinstance(listener_result, int) else 503
                    self.send_response(code)
                    self.end_headers()
                    return
            # perform the actual invocation of the backend service
            if response is None:
                if modified_request:
                    response = self.method(proxy_url, data=modified_request.data,
                        headers=modified_request.headers)
                else:
                    response = self.method(proxy_url, data=self.data_bytes,
                        headers=forward_headers)
            # update listener (post-invocation)
            if self.proxy.update_listener:
                kwargs = {
                    'method': method,
                    'path': path,
                    'data': data,
                    'headers': forward_headers,
                    'response': response
                }
                if 'request_handler' in inspect.getargspec(self.proxy.update_listener.return_response)[0]:
                    # some listeners (e.g., sqs_listener.py) require additional details like the original
                    # request port, hence we pass in a reference to this request handler as well.
                    kwargs['request_handler'] = self
                updated_response = self.proxy.update_listener.return_response(**kwargs)
                if isinstance(updated_response, Response):
                    response = updated_response

            # copy headers and return response
            self.send_response(response.status_code)

            content_length_sent = False
            for header_key, header_value in iteritems(response.headers):
                # filter out certain headers that we don't want to transmit
                if header_key not in ['Transfer-Encoding']:
                    self.send_header(header_key, header_value)
                    content_length_sent = content_length_sent or header_key.lower() == 'content-length'
            if not content_length_sent:
                self.send_header('Content-Length', '%s' % len(response.content) if response.content else 0)

            # allow pre-flight CORS headers by default
            if 'Access-Control-Allow-Origin' not in response.headers:
                self.send_header('Access-Control-Allow-Origin', '*')
            if 'Access-Control-Allow-Methods' not in response.headers:
                self.send_header('Access-Control-Allow-Methods', ','.join(CORS_ALLOWED_METHODS))
            if 'Access-Control-Allow-Headers' not in response.headers:
                self.send_header('Access-Control-Allow-Headers', ','.join(CORS_ALLOWED_HEADERS))

            self.end_headers()
            if response.content and len(response.content):
                self.wfile.write(to_bytes(response.content))
            self.wfile.flush()
        except Exception as e:
            trace = str(traceback.format_exc())
            conn_errors = ('ConnectionRefusedError', 'NewConnectionError')
            conn_error = any(e in trace for e in conn_errors)
            error_msg = 'Error forwarding request: %s %s' % (e, trace)
            if 'Broken pipe' in trace:
                LOGGER.warn('Connection prematurely closed by client (broken pipe).')
            elif not self.proxy.quiet or not conn_error:
                LOGGER.error(error_msg)
                if os.environ.get(ENV_INTERNAL_TEST_RUN):
                    # During a test run, we also want to print error messages, because
                    # log messages are delayed until the entire test run is over, and
                    # hence we are missing messages if the test hangs for some reason.
                    print('ERROR: %s' % error_msg)
            self.send_response(502)  # bad gateway
            self.end_headers()