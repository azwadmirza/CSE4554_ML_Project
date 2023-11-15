    def _infer_series_func_returns(self, df):
        try:
            empty_series = build_series(df, size=2, name=df.name)
            with np.errstate(all='ignore'):
                infer_series = empty_series.apply(self._func, args=self.args, **self.kwds)
            new_dtype = infer_series.dtype
            name = infer_series.name
        except:  # noqa: E722  # nosec  # pylint: disable=bare-except
            new_dtype = np.dtype('object')
            name = None
        return new_dtype, name