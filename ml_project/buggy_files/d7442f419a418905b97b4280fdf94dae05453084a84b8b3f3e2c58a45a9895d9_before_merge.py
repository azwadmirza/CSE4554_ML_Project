    def output(
            self, version="1.1", keep_alive=False, keep_alive_timeout=None):
        # This is all returned in a kind-of funky way
        # We tried to make this as fast as possible in pure python
        timeout_header = b''
        if keep_alive and keep_alive_timeout is not None:
            timeout_header = b'Keep-Alive: %d\r\n' % keep_alive_timeout

        body = b''
        if http.has_message_body(self.status):
            body = self.body
            self.headers['Content-Length'] = self.headers.get(
                'Content-Length', len(self.body))

        self.headers['Content-Type'] = self.headers.get(
                                       'Content-Type', self.content_type)

        if self.status in (304, 412):
            self.headers = http.remove_entity_headers(self.headers)

        headers = self._parse_headers()

        if self.status is 200:
            status = b'OK'
        else:
            status = http.STATUS_CODES.get(self.status, b'UNKNOWN RESPONSE')

        return (b'HTTP/%b %d %b\r\n'
                b'Connection: %b\r\n'
                b'%b'
                b'%b\r\n'
                b'%b') % (
                   version.encode(),
                   self.status,
                   status,
                   b'keep-alive' if keep_alive else b'close',
                   timeout_header,
                   headers,
                   body
               )