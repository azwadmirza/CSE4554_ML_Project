    def _call_series(self, series):
        if self._convert_dtype:
            dtype, name = self._infer_series_func_returns(series)
        else:
            dtype, name = np.dtype('object'), None
        return self.new_series([series], dtype=dtype, shape=series.shape,
                               index_value=series.index_value, name=name)