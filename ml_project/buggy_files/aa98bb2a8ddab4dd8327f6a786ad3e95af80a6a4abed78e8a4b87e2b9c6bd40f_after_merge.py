    def _getitem_axis(self, key, axis=None):
        if axis is None:
            axis = self.axis or 0

        if isinstance(key, slice):
            return self._get_slice_axis(key, axis=axis)

        if isinstance(key, list):
            key = np.asarray(key)

        if com.is_bool_indexer(key):
            self._validate_key(key, axis)
            return self._getbool_axis(key, axis=axis)

        # a list of integers
        elif is_list_like_indexer(key):
            return self._get_list_axis(key, axis=axis)

        # a single integer
        else:
            key = self._convert_scalar_indexer(key, axis)

            if not is_integer(key):
                raise TypeError("Cannot index by location index with a "
                                "non-integer key")

            # validate the location
            self._validate_integer(key, axis)

            return self._get_loc(key, axis=axis)