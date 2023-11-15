    def forward(self, method):
        path = self.path
        if '://' in path:
            path = '/' + path.split('://', 1)[1].split('/', 1)[1]
        proxy_url = 'http://%s%s' % (self.proxy.forward_host, path)
        target_url = self.path
        if '://' not in target_url:
            target_url = 'http://%s%s' % (self.proxy.forward_host, target_url)
        data = None
        if method in ['POST', 'PUT', 'PATCH']:
            data_string = self.data_bytes
            try:
                if not isinstance(data_string, string_types):
                    data_string = data_string.decode(DEFAULT_ENCODING)
                data = json.loads(data_string)
            except Exception as e:
                # unable to parse JSON, fallback to verbatim string/bytes
                data = data_string

        forward_headers = dict(self.headers)
        # update original "Host" header
        forward_headers['host'] = urlparse(target_url).netloc
        try:
            response = None
            modified_request = None
            # update listener (pre-invocation)
            if self.proxy.update_listener:
                listener_result = self.proxy.update_listener(method=method, path=path,
                    data=data, headers=forward_headers, return_forward_info=True)
                if isinstance(listener_result, Response):
                    response = listener_result
                elif isinstance(listener_result, Request):
                    modified_request = listener_result
                elif listener_result is not True:
                    # get status code from response, or use Bad Gateway status code
                    code = listener_result if isinstance(listener_result, int) else 503
                    self.send_response(code)
                    self.end_headers()
                    return
            if response is None:
                if modified_request:
                    response = self.method(proxy_url, data=modified_request.data,
                        headers=modified_request.headers)
                else:
                    response = self.method(proxy_url, data=self.data_bytes,
                        headers=forward_headers)
            # update listener (post-invocation)
            if self.proxy.update_listener:
                updated_response = self.proxy.update_listener(method=method, path=path,
                    data=data, headers=self.headers, response=response)
                if isinstance(updated_response, Response):
                    response = updated_response
            # copy headers and return response
            self.send_response(response.status_code)
            for header_key, header_value in iteritems(response.headers):
                self.send_header(header_key, header_value)
            self.end_headers()
            self.wfile.write(bytes_(response.content))
        except Exception as e:
            if not self.proxy.quiet:
                LOGGER.exception("Error forwarding request: %s" % str(e))