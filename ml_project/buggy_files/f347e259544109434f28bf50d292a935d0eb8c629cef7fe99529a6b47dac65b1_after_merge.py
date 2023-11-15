    def _calc_renamed_df(self, df, errors='ignore'):
        empty_df = build_df(df)
        return empty_df.rename(columns=self._columns_mapper, index=self._index_mapper,
                               level=self._level, errors=errors)