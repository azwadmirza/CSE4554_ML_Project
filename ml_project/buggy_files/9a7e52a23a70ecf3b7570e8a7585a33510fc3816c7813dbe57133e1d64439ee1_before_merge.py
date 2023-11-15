    def _get_dtype(self):
        if self._dtype_cache is None:
            map_func = self._prepare_method(lambda df: df.dtypes)

            def dtype_builder(df):
                return df.apply(lambda row: find_common_type(row.values), axis=0)

            self._dtype_cache = self._full_reduce(0, map_func, dtype_builder)
            self._dtype_cache.index = self.columns
        elif not self._dtype_cache.index.equals(self.columns):
            self._dtype_cache.index = self.columns
        return self._dtype_cache