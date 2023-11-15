    def get_headers(
            self, version="1.1", keep_alive=False, keep_alive_timeout=None):
        # This is all returned in a kind-of funky way
        # We tried to make this as fast as possible in pure python
        timeout_header = b''
        if keep_alive and keep_alive_timeout is not None:
            timeout_header = b'Keep-Alive: %d\r\n' % keep_alive_timeout

        self.headers['Transfer-Encoding'] = 'chunked'
        self.headers.pop('Content-Length', None)
        self.headers['Content-Type'] = self.headers.get(
            'Content-Type', self.content_type)

        headers = self._parse_headers()

        if self.status is 200:
            status = b'OK'
        else:
            status = STATUS_CODES.get(self.status)

        return (b'HTTP/%b %d %b\r\n'
                b'%b'
                b'%b\r\n') % (
                   version.encode(),
                   self.status,
                   status,
                   timeout_header,
                   headers
               )