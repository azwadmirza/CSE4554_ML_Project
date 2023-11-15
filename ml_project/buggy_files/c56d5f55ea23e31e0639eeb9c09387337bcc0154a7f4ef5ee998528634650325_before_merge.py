    def _encode_chunk(self, chunk):

        # apply filters
        if self._filters:
            for f in self._filters:
                chunk = f.encode(chunk)

        # check object encoding
        if isinstance(chunk, np.ndarray) and chunk.dtype == object:
            raise RuntimeError('cannot write object array without object codec')

        # compress
        if self._compressor:
            cdata = self._compressor.encode(chunk)
        else:
            cdata = chunk

        return cdata