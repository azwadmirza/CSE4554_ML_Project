    def __call__(self, df):
        if self.col_names is not None:
            # if col_names is a list, return a DataFrame, else return a Series
            if isinstance(self._col_names, list):
                dtypes = df.dtypes[self._col_names]
                columns = parse_index(pd.Index(self._col_names), store_data=True)
                return self.new_dataframe([df], shape=(df.shape[0], len(self._col_names)), dtypes=dtypes,
                                          index_value=df.index_value, columns_value=columns)
            else:
                dtype = df.dtypes[self._col_names]
                return self.new_series([df], shape=(df.shape[0],), dtype=dtype, index_value=df.index_value,
                                       name=self._col_names)
        else:
            if isinstance(self.mask, (SERIES_TYPE, DATAFRAME_TYPE)):
                index_value = parse_index(pd.Index([], dtype=df.index_value.to_pandas().dtype),
                                          df, self._mask)
                return self.new_dataframe([df, self._mask], shape=(np.nan, df.shape[1]), dtypes=df.dtypes,
                                          index_value=index_value, columns_value=df.columns_value)
            else:
                index_value = parse_index(pd.Index([], dtype=df.index_value.to_pandas().dtype),
                                          df, self._mask)
                return self.new_dataframe([df], shape=(np.nan, df.shape[1]), dtypes=df.dtypes,
                                          index_value=index_value, columns_value=df.columns_value)