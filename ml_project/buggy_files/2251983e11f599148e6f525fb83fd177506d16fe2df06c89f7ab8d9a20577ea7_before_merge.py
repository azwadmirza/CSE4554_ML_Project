    def _call_series(self, series):
        if self._convert_dtype:
            dtype = self._infer_series_func_returns(series.dtype)
        else:
            dtype = np.dtype('object')
        return self.new_series([series], dtype=dtype, shape=series.shape,
                               index_value=series.index_value)