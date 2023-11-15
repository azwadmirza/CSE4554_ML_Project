    def take(self, indices, axis=0):
        """
        Sparse-compatible version of ndarray.take

        Returns
        -------
        taken : ndarray
        """
        if axis:
            raise ValueError("axis must be 0, input was {0}".format(axis))

        if com.is_integer(indices):
            # return scalar
            return self[indices]

        indices = np.atleast_1d(np.asarray(indices, dtype=int))

        # allow -1 to indicate missing values
        n = len(self)
        if ((indices >= n) | (indices < -1)).any():
            raise IndexError('out of bounds access')

        if self.sp_index.npoints > 0:
            locs = np.array([self.sp_index.lookup(loc) if loc > -1 else -1
                             for loc in indices])
            result = self.sp_values.take(locs)
            mask = locs == -1
            if mask.any():
                try:
                    result[mask] = self.fill_value
                except ValueError:
                    # wrong dtype
                    result = result.astype('float64')
                    result[mask] = self.fill_value

        else:
            result = np.empty(len(indices))
            result.fill(self.fill_value)

        return self._constructor(result)