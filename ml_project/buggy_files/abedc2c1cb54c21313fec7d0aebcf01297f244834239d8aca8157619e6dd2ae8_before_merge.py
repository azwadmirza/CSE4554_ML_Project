    def sum(self, axis=None):
        """Sum the matrix over the given axis.  If the axis is None, sum
        over both rows and columns, returning a scalar.
        """
        # The spmatrix base class already does axis=0 and axis=1 efficiently
        # so we only do the case axis=None here
        if axis is None:
            return self.data.sum()
        elif (not hasattr(self, 'blocksize') and
              axis in self._swap(((1, -1), (0, 2)))[0]):
            # faster than multiplication for large minor axis in CSC/CSR
            # Mimic numpy's casting.
            if np.issubdtype(self.dtype, np.float_):
                res_dtype = np.float_
            elif self.dtype.kind in 'ib':
                res_dtype = np.int_
            elif self.dtype.kind == 'u':
                res_dtype = np.uint
            else:
                res_dtype = self.dtype
            ret = np.zeros(len(self.indptr) - 1, dtype=res_dtype)

            major_index, value = self._minor_reduce(np.add)
            ret[major_index] = value
            ret = np.asmatrix(ret)
            if axis % 2 == 1:
                ret = ret.T
            return ret
        else:
            return spmatrix.sum(self, axis)