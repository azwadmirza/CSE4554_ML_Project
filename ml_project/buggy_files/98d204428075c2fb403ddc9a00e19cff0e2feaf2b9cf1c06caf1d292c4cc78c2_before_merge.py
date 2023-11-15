    def __setitem__(self, key, value):
        if isinstance(value, (pd.Index, pd.Series)):
            value = value.to_numpy()

        key = check_array_indexer(self, key)
        scalar_key = is_scalar(key)

        # validate new items
        if scalar_key:
            if pd.isna(value):
                value = None
            elif not is_list_like(value):
                raise ValueError('Must provide list.')

        array = np.asarray(self._arrow_array.to_pandas())
        array[key] = value
        self._arrow_array = pa.chunked_array([
            pa.array(array, type=self.dtype.arrow_type)])