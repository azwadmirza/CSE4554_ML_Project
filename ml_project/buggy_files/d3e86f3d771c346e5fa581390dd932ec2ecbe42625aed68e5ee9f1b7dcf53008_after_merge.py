    def _getitem_iterable(self, key, axis=0):
        labels = self.obj._get_axis(axis)

        def _reindex(keys, level=None):
            try:
                return self.obj.reindex_axis(keys, axis=axis, level=level)
            except AttributeError:
                # Series
                assert(axis == 0)
                return self.obj.reindex(keys, level=level)

        if com._is_bool_indexer(key):
            key = _check_bool_indexer(labels, key)
            return _reindex(labels[np.asarray(key)])
        else:
            if isinstance(key, Index):
                # want Index objects to pass through untouched
                keyarr = key
            else:
                # asarray can be unsafe, NumPy strings are weird
                keyarr = _asarray_tuplesafe(key)

            if _is_integer_dtype(keyarr) and not _is_integer_index(labels):
                return self.obj.take(keyarr, axis=axis)

            # this is not the most robust, but...
            if (isinstance(labels, MultiIndex) and
                not isinstance(keyarr[0], tuple)):
                level = 0
            else:
                level = None

            return _reindex(keyarr, level=level)