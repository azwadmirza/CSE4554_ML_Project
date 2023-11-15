    def diagonal(self, k=0):
        rows, cols = self.shape
        if k <= -rows or k >= cols:
            raise ValueError("k exceeds matrix dimensions")
        idx, = np.nonzero(self.offsets == k)
        first_col, last_col = max(0, k), min(rows + k, cols)
        if idx.size == 0:
            return np.zeros(last_col - first_col, dtype=self.data.dtype)
        return self.data[idx[0], first_col:last_col]