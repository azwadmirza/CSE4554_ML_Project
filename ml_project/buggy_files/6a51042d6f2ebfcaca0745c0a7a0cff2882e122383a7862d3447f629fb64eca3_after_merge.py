    def __setitem__(self, key, value) -> None:
        value = extract_array(value, extract_numpy=True)

        key = check_array_indexer(self, key)
        scalar_value = lib.is_scalar(value)

        if not scalar_value:
            value = np.asarray(value, dtype=self._ndarray.dtype)

        self._ndarray[key] = value