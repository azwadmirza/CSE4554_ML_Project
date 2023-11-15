    def nbytes(self) -> int:
        if self._use_arrow:
            return sum(x.size
                       for chunk in self._arrow_array.chunks
                       for x in chunk.buffers()
                       if x is not None)
        else:
            return self._ndarray.nbytes