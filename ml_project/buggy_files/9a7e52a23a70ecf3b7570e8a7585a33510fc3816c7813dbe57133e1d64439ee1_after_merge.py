    def _get_dtype(self):
        calculate_dtype = False
        if self._dtype_cache is None:
            calculate_dtype = True
        else:
            if len(self.columns) != len(self._dtype_cache):
                if all(col in self._dtype_cache.index for col in self.columns):
                    self._dtype_cache = pandas.Series(
                        {col: self._dtype_cache[col] for col in self.columns}
                    )
                else:
                    calculate_dtype = True
            elif not self._dtype_cache.equals(self.columns):
                self._dtype_cache.index = self.columns
        if calculate_dtype:
            map_func = self._prepare_method(lambda df: df.dtypes)

            def dtype_builder(df):
                return df.apply(lambda row: find_common_type(row.values), axis=0)

            self._dtype_cache = self._full_reduce(0, map_func, dtype_builder)
            self._dtype_cache.index = self.columns
        return self._dtype_cache