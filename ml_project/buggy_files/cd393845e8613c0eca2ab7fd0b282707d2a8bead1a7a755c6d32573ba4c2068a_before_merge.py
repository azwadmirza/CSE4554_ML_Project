    def _infer_df_func_returns(self, in_dtypes, dtypes, index):
        if isinstance(self._func, np.ufunc):
            output_type, new_dtypes, index_value, new_elementwise = \
                OutputType.dataframe, None, 'inherit', True
        else:
            output_type, new_dtypes, index_value, new_elementwise = None, None, None, False

        try:
            empty_df = build_empty_df(in_dtypes, index=pd.RangeIndex(2))
            with np.errstate(all='ignore'):
                infer_df = empty_df.apply(self._func, axis=self._axis, raw=self._raw,
                                          result_type=self._result_type, args=self.args, **self.kwds)
            if index_value is None:
                if infer_df.index is empty_df.index:
                    index_value = 'inherit'
                else:
                    index_value = parse_index(pd.RangeIndex(-1))

            if isinstance(infer_df, pd.DataFrame):
                output_type = output_type or OutputType.dataframe
                new_dtypes = new_dtypes or infer_df.dtypes
            else:
                output_type = output_type or OutputType.series
                new_dtypes = new_dtypes or infer_df.dtype
            new_elementwise = False if new_elementwise is None else new_elementwise
        except:  # noqa: E722  # nosec
            pass

        self.output_types = [output_type] if not self.output_types else self.output_types
        dtypes = new_dtypes if dtypes is None else dtypes
        index_value = index_value if index is None else parse_index(index)
        self._elementwise = new_elementwise if self._elementwise is None else self._elementwise
        return dtypes, index_value