    def _min_or_max(self, axis, out, min_or_max, sum_duplicates, non_zero):
        if out is not None:
            raise ValueError(("Sparse matrices do not support "
                              "an 'out' parameter."))

        util.validateaxis(axis)

        if axis is None:
            if 0 in self.shape:
                raise ValueError("zero-size array to reduction operation")

            zero = cupy.zeros((), dtype=self.dtype)
            if self.nnz == 0:
                return zero
            if sum_duplicates:
                self.sum_duplicates()
            m = min_or_max(self.data)
            if non_zero:
                return m
            if self.nnz != internal.prod(self.shape):
                if min_or_max is cupy.min:
                    m = cupy.minimum(zero, m)
                elif min_or_max is cupy.max:
                    m = cupy.maximum(zero, m)
                else:
                    assert False
            return m

        if axis == 0 or axis == 1:
            return self._min_or_max_axis(axis, min_or_max, sum_duplicates,
                                         non_zero)
        else:
            raise ValueError("axis out of range")