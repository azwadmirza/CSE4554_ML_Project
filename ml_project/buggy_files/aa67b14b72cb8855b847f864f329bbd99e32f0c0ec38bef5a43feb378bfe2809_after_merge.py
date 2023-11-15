    def _set_with(self, key, value):
        # other: fancy integer or otherwise
        if isinstance(key, slice):
            indexer = self.index._convert_slice_indexer(key, kind="getitem")
            return self._set_values(indexer, value)
        else:
            if isinstance(key, tuple):
                try:
                    self._set_values(key, value)
                except Exception:
                    pass

            if is_scalar(key) and not is_integer(key) and key not in self.index:
                # GH#12862 adding an new key to the Series
                # Note: have to exclude integers because that is ambiguously
                #  position-based
                self.loc[key] = value
                return

            if is_scalar(key):
                key = [key]
            elif not isinstance(key, (list, Series, np.ndarray)):
                try:
                    key = list(key)
                except Exception:
                    key = [key]

            if isinstance(key, Index):
                key_type = key.inferred_type
            else:
                key_type = lib.infer_dtype(key, skipna=False)

            if key_type == "integer":
                if self.index.inferred_type == "integer":
                    self._set_labels(key, value)
                else:
                    return self._set_values(key, value)
            elif key_type == "boolean":
                self._set_values(key.astype(np.bool_), value)
            else:
                self._set_labels(key, value)