    def _infer_df_func_returns(self, df, dtypes):
        if self.output_types[0] == OutputType.dataframe:
            test_df = build_df(df, fill_value=1, size=2)
            try:
                with np.errstate(all='ignore'):
                    if self.call_agg:
                        infer_df = test_df.agg(self._func, axis=self._axis, *self.args, **self.kwds)
                    else:
                        infer_df = test_df.transform(self._func, axis=self._axis, *self.args, **self.kwds)
            except:  # noqa: E722
                infer_df = None
        else:
            test_df = build_series(df, size=2, name=df.name)
            try:
                with np.errstate(all='ignore'):
                    if self.call_agg:
                        infer_df = test_df.agg(self._func, args=self.args, **self.kwds)
                    else:
                        infer_df = test_df.transform(self._func, convert_dtype=self.convert_dtype,
                                                      args=self.args, **self.kwds)
            except:  # noqa: E722
                infer_df = None

        if infer_df is None and dtypes is None:
            raise TypeError('Failed to infer dtype, please specify dtypes as arguments.')

        if infer_df is None:
            is_df = self.output_types[0] == OutputType.dataframe
        else:
            is_df = isinstance(infer_df, pd.DataFrame)

        if is_df:
            new_dtypes = dtypes or infer_df.dtypes
            self.output_types = [OutputType.dataframe]
        else:
            new_dtypes = dtypes or (infer_df.name, infer_df.dtype)
            self.output_types = [OutputType.series]

        return new_dtypes