    def __mars_tokenize__(self):
        return [memoryview(x) for chunk in self._arrow_array.chunks
                for x in chunk.buffers()
                if x is not None]