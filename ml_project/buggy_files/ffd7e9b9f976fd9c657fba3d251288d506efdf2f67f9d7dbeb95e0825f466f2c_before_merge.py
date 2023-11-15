    def diagonal(self, k=0):
        rows, cols = self.shape
        if k <= -rows or k >= cols:
            raise ValueError("k exceeds matrix dimensions")
        diag = np.zeros(min(rows + min(k, 0), cols - max(k, 0)),
                        dtype=self.dtype)
        diag_mask = (self.row + k) == self.col

        if self.has_canonical_format:
            row = self.row[diag_mask]
            data = self.data[diag_mask]
        else:
            row, _, data = self._sum_duplicates(self.row[diag_mask],
                                                self.col[diag_mask],
                                                self.data[diag_mask])
        diag[row + min(k, 0)] = data

        return diag