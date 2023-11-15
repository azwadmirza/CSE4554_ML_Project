    def _infer_df_func_returns(self, in_dtypes, dtypes):
        if self.output_types[0] == OutputType.dataframe:
            empty_df = build_empty_df(in_dtypes, index=pd.RangeIndex(2))
            with np.errstate(all='ignore'):
                if self.call_agg:
                    infer_df = empty_df.agg(self._func, axis=self._axis, *self.args, **self.kwds)
                else:
                    infer_df = empty_df.transform(self._func, axis=self._axis, *self.args, **self.kwds)
        else:
            empty_df = build_empty_series(in_dtypes[1], index=pd.RangeIndex(2), name=in_dtypes[0])
            with np.errstate(all='ignore'):
                if self.call_agg:
                    infer_df = empty_df.agg(self._func, args=self.args, **self.kwds)
                else:
                    infer_df = empty_df.transform(self._func, convert_dtype=self.convert_dtype,
                                                  args=self.args, **self.kwds)

        if isinstance(infer_df, pd.DataFrame):
            new_dtypes = dtypes or infer_df.dtypes
            self.output_types = [OutputType.dataframe]
        else:
            new_dtypes = dtypes or (infer_df.name, infer_df.dtype)
            self.output_types = [OutputType.series]

        return new_dtypes