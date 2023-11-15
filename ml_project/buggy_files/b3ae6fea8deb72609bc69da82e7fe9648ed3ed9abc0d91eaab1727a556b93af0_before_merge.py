    def diagonal(self, k=0):
        rows, cols = self.shape
        if k <= -rows or k >= cols:
            raise ValueError("k exceeds matrix dimensions")
        fn = getattr(_sparsetools, self.format + "_diagonal")
        y = np.empty(min(rows + min(k, 0), cols - max(k, 0)),
                     dtype=upcast(self.dtype))
        fn(k, self.shape[0], self.shape[1], self.indptr, self.indices,
           self.data, y)
        return y