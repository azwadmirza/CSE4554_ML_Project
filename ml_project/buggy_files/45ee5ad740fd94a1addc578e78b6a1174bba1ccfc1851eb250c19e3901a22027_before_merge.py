    def value_counts(self, dropna=False):
        series = self._arrow_array.to_pandas()
        return type(self)(series.value_counts(dropna=dropna),
                          dtype=self._dtype)