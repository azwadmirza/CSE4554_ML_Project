    def _stream_helper(self, response):
        """Generator for data coming from a chunked-encoded HTTP response."""
        socket_fp = self._get_raw_response_socket(response)
        socket_fp.setblocking(1)
        socket = socket_fp.makefile()
        while True:
            size = int(socket.readline(), 16)
            if size <= 0:
                break
            data = socket.readline()
            if not data:
                break
            yield data