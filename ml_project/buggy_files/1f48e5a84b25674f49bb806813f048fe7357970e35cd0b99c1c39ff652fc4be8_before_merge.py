    def _call_dataframe(self, a):
        if self.drop:
            shape = a.shape
            columns_value = a.columns_value
            dtypes = a.dtypes
            range_value = -1 if np.isnan(a.shape[0]) else a.shape[0]
            index_value = parse_index(pd.RangeIndex(range_value))
        else:
            empty_df = build_empty_df(a.dtypes)
            empty_df.index = a.index_value.to_pandas()[:0]
            empty_df = empty_df.reset_index(level=self.level, col_level=self.col_level, col_fill=self.col_fill)
            shape = (a.shape[0], len(empty_df.columns))
            columns_value = parse_index(empty_df.columns)
            dtypes = empty_df.dtypes
            index_value = self._get_out_index(empty_df, shape)
        return self.new_dataframe([a], shape=shape, columns_value=columns_value,
                                  index_value=index_value, dtypes=dtypes)