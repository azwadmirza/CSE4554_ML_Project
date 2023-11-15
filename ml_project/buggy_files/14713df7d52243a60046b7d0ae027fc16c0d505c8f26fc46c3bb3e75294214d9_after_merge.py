    def _getitem_axis(self, key, axis=None):

        if axis is None:
            axis = self.axis or 0

        if is_iterator(key):
            key = list(key)
        self._validate_key(key, axis)

        labels = self.obj._get_axis(axis)
        if isinstance(key, slice):
            return self._get_slice_axis(key, axis=axis)
        elif (is_list_like_indexer(key) and
              not (isinstance(key, tuple) and
                   isinstance(labels, MultiIndex))):

            if hasattr(key, 'ndim') and key.ndim > 1:
                raise ValueError('Cannot index with multidimensional key')

            return self._getitem_iterable(key, axis=axis)
        else:

            # maybe coerce a float scalar to integer
            key = labels._maybe_cast_indexer(key)

            if is_integer(key):
                if axis == 0 and isinstance(labels, MultiIndex):
                    try:
                        return self._get_label(key, axis=axis)
                    except (KeyError, TypeError):
                        if self.obj.index.levels[0].is_integer():
                            raise

                # this is the fallback! (for a non-float, non-integer index)
                if not labels.is_floating() and not labels.is_integer():
                    return self._get_loc(key, axis=axis)

            return self._get_label(key, axis=axis)