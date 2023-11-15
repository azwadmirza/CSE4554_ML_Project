    def _stream_helper(self, response):
        """Generator for data coming from a chunked-encoded HTTP response."""
        reader = response.raw
        assert reader._fp.chunked
        while not reader.closed:
            # this read call will block until we get a chunk
            data = reader.read(1)
            if not data:
                break
            if reader._fp.chunk_left:
                data += reader.read(reader._fp.chunk_left)
            yield data