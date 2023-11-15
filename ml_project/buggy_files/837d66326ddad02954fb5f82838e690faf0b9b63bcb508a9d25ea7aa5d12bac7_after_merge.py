    def _getitem_axis(self, key, axis=None):
        if axis is None:
            axis = self.axis or 0

        if is_iterator(key):
            key = list(key)

        labels = self.obj._get_axis(axis)
        key = self._get_partial_string_timestamp_match_key(key, labels)

        if isinstance(key, slice):
            self._validate_key(key, axis)
            return self._get_slice_axis(key, axis=axis)
        elif com.is_bool_indexer(key):
            return self._getbool_axis(key, axis=axis)
        elif is_list_like_indexer(key):

            # convert various list-like indexers
            # to a list of keys
            # we will use the *values* of the object
            # and NOT the index if its a PandasObject
            if isinstance(labels, MultiIndex):

                if isinstance(key, (ABCSeries, np.ndarray)) and key.ndim <= 1:
                    # Series, or 0,1 ndim ndarray
                    # GH 14730
                    key = list(key)
                elif isinstance(key, ABCDataFrame):
                    # GH 15438
                    raise NotImplementedError("Indexing a MultiIndex with a "
                                              "DataFrame key is not "
                                              "implemented")
                elif hasattr(key, 'ndim') and key.ndim > 1:
                    raise NotImplementedError("Indexing a MultiIndex with a "
                                              "multidimensional key is not "
                                              "implemented")

                if (not isinstance(key, tuple) and len(key) > 1 and
                        not isinstance(key[0], tuple)):
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
        self._validate_key(key, axis)
        return self._get_label(key, axis=axis)