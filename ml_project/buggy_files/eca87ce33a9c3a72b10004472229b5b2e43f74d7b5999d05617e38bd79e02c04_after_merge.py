    def _send_request(self, method, url, body, headers, *args, **kwargs):
        self._response_received = False
        if headers.get('Expect', b'') == b'100-continue':
            self._expect_header_set = True
        else:
            self._expect_header_set = False
            self.response_class = self._original_response_cls
        rval = HTTPConnection._send_request(
            self, method, url, body, headers, *args, **kwargs)
        self._expect_header_set = False
        return rval