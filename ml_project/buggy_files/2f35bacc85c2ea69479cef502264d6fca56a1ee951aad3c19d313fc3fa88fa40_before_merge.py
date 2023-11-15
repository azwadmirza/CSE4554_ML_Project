    def _infer_series_func_returns(self, in_dtype):
        try:
            empty_series = build_empty_series(in_dtype, index=pd.RangeIndex(2))
            with np.errstate(all='ignore'):
                infer_series = empty_series.apply(self._func, args=self.args, **self.kwds)
            new_dtype = infer_series.dtype
        except:  # noqa: E722  # nosec  # pylint: disable=bare-except
            new_dtype = np.dtype('object')
        return new_dtype