    def _infer_df_func_returns(self, in_groupby, in_df, dtypes, index):
        index_value, output_type, new_dtypes = None, None, None

        try:
            if in_df.op.output_types[0] == OutputType.dataframe:
                empty_df = build_empty_df(in_df.dtypes, index=pd.RangeIndex(2))
            else:
                empty_df = build_empty_series(in_df.dtype, index=pd.RangeIndex(2), name=in_df.name)

            selection = getattr(in_groupby.op, 'selection', None)
            if selection:
                empty_df = empty_df[selection]

            with np.errstate(all='ignore'):
                infer_df = self.func(empty_df, *self.args, **self.kwds)

            # todo return proper index when sort=True is implemented
            index_value = parse_index(None, in_df.key, self.func)

            if isinstance(infer_df, pd.DataFrame):
                output_type = output_type or OutputType.dataframe
                new_dtypes = new_dtypes or infer_df.dtypes
            elif isinstance(infer_df, pd.Series):
                output_type = output_type or OutputType.series
                new_dtypes = new_dtypes or (infer_df.name, infer_df.dtype)
            else:
                output_type = OutputType.series
                new_dtypes = (None, pd.Series(infer_df).dtype)
        except:  # noqa: E722  # nosec
            pass

        self.output_types = [output_type] if not self.output_types else self.output_types
        dtypes = new_dtypes if dtypes is None else dtypes
        index_value = index_value if index is None else parse_index(index)
        return dtypes, index_value