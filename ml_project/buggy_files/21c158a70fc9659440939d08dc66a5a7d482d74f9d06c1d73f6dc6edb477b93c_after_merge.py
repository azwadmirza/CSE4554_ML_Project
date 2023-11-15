    def _calc_renamed_series(self, df, errors='ignore'):
        empty_series = build_series(df, name=df.name)
        new_series = empty_series.rename(index=self._index_mapper, level=self._level, errors=errors)
        if self._new_name:
            new_series.name = self._new_name
        return new_series