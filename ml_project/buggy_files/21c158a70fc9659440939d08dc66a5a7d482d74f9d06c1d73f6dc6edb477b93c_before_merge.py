    def _calc_renamed_series(self, name, dtype, index, errors='ignore'):
        empty_series = build_empty_series(dtype, index=index, name=name)
        new_series = empty_series.rename(index=self._index_mapper, level=self._level, errors=errors)
        if self._new_name:
            new_series.name = self._new_name
        return new_series