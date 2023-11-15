    def _stream_helper(self, response):
        """Generator for data coming from a chunked-encoded HTTP response."""
        socket_fp = self._get_raw_response_socket(response)
        socket_fp.setblocking(1)
        socket = socket_fp.makefile()
        while True:
            # Because Docker introduced newlines at the end of chunks in v0.9,
            # and only on some API endpoints, we have to cater for both cases.
            size_line = socket.readline()
            if size_line == '\r\n':
                size_line = socket.readline()

            size = int(size_line, 16)
            if size <= 0:
                break
            data = socket.readline()
            if not data:
                break
            yield data