    def _calc_renamed_df(self, dtypes, index, errors='ignore'):
        empty_df = build_empty_df(dtypes, index=index)
        return empty_df.rename(columns=self._columns_mapper, index=self._index_mapper,
                               level=self._level, errors=errors)