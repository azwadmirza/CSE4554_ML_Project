    def fillna(self, value=None, method='pad', inplace=False):
        new_series = {}
        for k, v in self.iterkv():
            new_series[k] = v.fillna(value=value, method=method)

        if inplace:
            self._series = new_series
            return self
        else:
            return self._constructor(new_series, index=self.index,
                                     columns=self.columns)