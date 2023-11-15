    def value_counts(self, dropna=False):
        if self._use_arrow:
            series = self._arrow_array.to_pandas()
        else:
            series = pd.Series(self._ndarray)
        return type(self)(series.value_counts(dropna=dropna),
                          dtype=self._dtype)