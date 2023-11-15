    def __setitem__(self, key, value):
        if isinstance(value, (pd.Index, pd.Series)):
            value = value.to_numpy()
        if isinstance(value, type(self)):
            value = value.to_numpy()

        key = check_array_indexer(self, key)
        scalar_key = is_scalar(key)
        scalar_value = is_scalar(value)
        if scalar_key and not scalar_value:
            raise ValueError("setting an array element with a sequence.")

        # validate new items
        if scalar_value:
            if pd.isna(value):
                value = None
            elif not isinstance(value, str):
                raise ValueError(
                    f"Cannot set non-string value '{value}' into a ArrowStringArray."
                )
        else:
            if not is_array_like(value):
                value = np.asarray(value, dtype=object)
            if len(value) and not lib.is_string_array(value, skipna=True):
                raise ValueError("Must provide strings.")

        string_array = np.asarray(self._arrow_array.to_pandas())
        string_array[key] = value
        self._arrow_array = pa.chunked_array([pa.array(string_array)])