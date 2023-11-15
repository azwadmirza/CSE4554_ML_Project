    def _get_with(self, key):
        # other: fancy integer or otherwise
        if isinstance(key, slice):
            from pandas.core.indexing import _is_index_slice

            if self.index.inferred_type == 'integer' or _is_index_slice(key):
                indexer = key
            else:
                indexer = self.ix._convert_to_indexer(key, axis=0)
            return self._get_values(indexer)
        else:
            if isinstance(key, tuple):
                return self._get_values_tuple(key)

            if not isinstance(key, (list, np.ndarray)):  # pragma: no cover
                key = list(key)

            key_type = lib.infer_dtype(key)

            if key_type == 'integer':
                if self.index.inferred_type == 'integer':
                    return self.reindex(key)
                else:
                    return self._get_values(key)
            elif key_type == 'boolean':
                return self._get_values(key)
            else:
                try:
                    return self.reindex(key)
                except Exception:
                    # [slice(0, 5, None)] will break if you convert to ndarray,
                    # e.g. as requested by np.median
                    # hack
                    if isinstance(key[0], slice):
                        return self._get_values(key)
                    raise