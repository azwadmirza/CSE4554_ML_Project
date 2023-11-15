    def diagonal(self, k=0):
        rows, cols = self.shape
        if k <= -rows or k >= cols:
            raise ValueError("k exceeds matrix dimensions")
        R, C = self.blocksize
        y = np.zeros(min(rows + min(k, 0), cols - max(k, 0)),
                     dtype=upcast(self.dtype))
        _sparsetools.bsr_diagonal(k, rows // R, cols // C, R, C,
                                  self.indptr, self.indices,
                                  np.ravel(self.data), y)
        return y