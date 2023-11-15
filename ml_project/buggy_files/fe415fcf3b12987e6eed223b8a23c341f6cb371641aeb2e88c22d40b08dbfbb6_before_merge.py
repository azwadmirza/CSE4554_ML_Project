    def _min_or_max(self, axis, out, min_or_max, sum_duplicates, non_zero):
        if out is not None:
            raise ValueError(("Sparse matrices do not support "
                              "an 'out' parameter."))

        util.validateaxis(axis)

        if axis == 0 or axis == 1:
            return self._min_or_max_axis(axis, min_or_max, sum_duplicates,
                                         non_zero)
        else:
            raise ValueError("axis out of range")