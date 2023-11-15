    def _stream_helper(self, response):
        """Generator for data coming from a chunked-encoded HTTP response."""
        for line in response.iter_lines(chunk_size=32):
            yield line