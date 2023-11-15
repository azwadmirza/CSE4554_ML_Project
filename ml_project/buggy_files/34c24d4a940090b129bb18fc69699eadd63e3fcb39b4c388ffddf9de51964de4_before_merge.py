    def _convert_for_reindex(self, key, axis=None):
        if axis is None:
            axis = self.axis or 0
        labels = self.obj._get_axis(axis)

        if com.is_bool_indexer(key):
            key = check_bool_indexer(labels, key)
            return labels[key]
        else:
            if isinstance(key, Index):
                keyarr = labels._convert_index_indexer(key)
            else:
                # asarray can be unsafe, NumPy strings are weird
                keyarr = com._asarray_tuplesafe(key)

            if is_integer_dtype(keyarr):
                # Cast the indexer to uint64 if possible so
                # that the values returned from indexing are
                # also uint64.
                keyarr = labels._convert_arr_indexer(keyarr)

                if not labels.is_integer():
                    keyarr = _ensure_platform_int(keyarr)
                    return labels.take(keyarr)

            return keyarr