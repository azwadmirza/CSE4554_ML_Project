    def _getitem_axis(self, key, axis=0):
        labels = self.obj._get_axis(axis)
        key = self._get_partial_string_timestamp_match_key(key, labels)

        if isinstance(key, slice):
            self._has_valid_type(key, axis)
            return self._get_slice_axis(key, axis=axis)
        elif is_bool_indexer(key):
            return self._getbool_axis(key, axis=axis)
        elif is_list_like_indexer(key):

            # GH 7349
            # possibly convert a list-like into a nested tuple
            # but don't convert a list-like of tuples
            if isinstance(labels, MultiIndex):
                if (not isinstance(key, tuple) and len(key) > 1 and
                        not isinstance(key[0], tuple)):
                    if isinstance(key, ABCSeries):
                        # GH 14730
                        key = list(key)
                    key = tuple([key])

            # an iterable multi-selection
            if not (isinstance(key, tuple) and isinstance(labels, MultiIndex)):

                if hasattr(key, 'ndim') and key.ndim > 1:
                    raise ValueError('Cannot index with multidimensional key')

                return self._getitem_iterable(key, axis=axis)

            # nested tuple slicing
            if is_nested_tuple(key, labels):
                locs = labels.get_locs(key)
                indexer = [slice(None)] * self.ndim
                indexer[axis] = locs
                return self.obj.iloc[tuple(indexer)]

        # fall thru to straight lookup
        self._has_valid_type(key, axis)
        return self._get_label(key, axis=axis)