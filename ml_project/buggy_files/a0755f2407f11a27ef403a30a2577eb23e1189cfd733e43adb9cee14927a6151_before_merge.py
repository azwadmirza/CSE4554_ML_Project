    def __call__(self, df_or_series):
        inputs = [df_or_series]
        shape = list(df_or_series.shape)
        index_value = df_or_series.index_value
        columns_value = dtypes = None
        if df_or_series.ndim == 2:
            columns_value = df_or_series.columns_value
            dtypes = df_or_series.dtypes

        if self._index is not None:
            shape[0] = self._index.shape[0]
            index_value = asindex(self._index).index_value
            if isinstance(self._index, (Base, Entity)):
                inputs.append(self._index)
        if self._columns is not None:
            shape[1] = self._columns.shape[0]
            dtypes = df_or_series.dtypes.reindex(index=self._columns).fillna(
                np.dtype(np.float64))
            columns_value = parse_index(dtypes.index, store_data=True)
        if self._fill_value is not None and \
                isinstance(self._fill_value, (Base, Entity)):
            inputs.append(self._fill_value)

        if df_or_series.ndim == 1:
            return self.new_series(inputs, shape=shape, dtype=df_or_series.dtype,
                                   index_value=index_value, name=df_or_series.name)
        else:
            return self.new_dataframe(inputs, shape=shape, dtypes=dtypes,
                                      index_value=index_value,
                                      columns_value=columns_value)