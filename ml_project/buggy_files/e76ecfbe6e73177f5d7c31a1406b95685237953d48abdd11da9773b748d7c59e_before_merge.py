    def sum(self, axis=None):
        """Sum the matrix over the given axis.  If the axis is None, sum
        over both rows and columns, returning a scalar.
        """
        # We use multiplication by an array of ones to achieve this.
        # For some sparse matrix formats more efficient methods are
        # possible -- these should override this function.
        m, n = self.shape

        # Mimic numpy's casting.
        if np.issubdtype(self.dtype, np.float_):
            res_dtype = np.float_
        elif self.dtype.kind in 'ib':
            res_dtype = np.int_
        elif self.dtype.kind == 'u':
            res_dtype = np.uint
        else:
            res_dtype = self.dtype

        if axis is None:
            # sum over rows and columns
            return (self * np.asmatrix(np.ones((n, 1), dtype=res_dtype))).sum()

        if axis < 0:
            axis += 2
        if axis == 0:
            # sum over columns
            return np.asmatrix(np.ones((1, m), dtype=res_dtype)) * self
        elif axis == 1:
            # sum over rows
            return self * np.asmatrix(np.ones((n, 1), dtype=res_dtype))
        else:
            raise ValueError("axis out of bounds")