    def __call__(self, df):
        params = df.params
        raw_index = df.index_value.to_pandas()
        if df.ndim == 2:
            new_df = self._calc_renamed_df(df.dtypes, raw_index, errors=self.errors)
            new_index = new_df.index
        elif isinstance(df, SERIES_TYPE):
            new_df = self._calc_renamed_series(df.name, df.dtype, raw_index, errors=self.errors)
            new_index = new_df.index
        else:
            new_df = new_index = raw_index.rename(self._index_mapper or self._new_name)

        if self._columns_mapper is not None:
            params['columns_value'] = parse_index(new_df.columns, store_data=True)
            params['dtypes'] = new_df.dtypes
        if self._index_mapper is not None:
            params['index_value'] = parse_index(new_index)
        if df.ndim == 1:
            params['name'] = new_df.name
        return self.new_tileable([df], **params)