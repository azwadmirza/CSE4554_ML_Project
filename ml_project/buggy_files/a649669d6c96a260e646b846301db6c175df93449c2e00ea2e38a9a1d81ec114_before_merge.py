    def nbytes(self) -> int:
        return sum(x.size
                   for chunk in self._arrow_array.chunks
                   for x in chunk.buffers()
                   if x is not None)