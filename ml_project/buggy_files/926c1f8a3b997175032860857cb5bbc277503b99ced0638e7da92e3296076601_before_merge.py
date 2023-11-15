    def _calc_result_shape(self, df):
        if self.output_types[0] == OutputType.dataframe:
            empty_obj = build_empty_df(df.dtypes, index=pd.RangeIndex(0, 10))
        else:
            empty_obj = build_empty_series(df.dtype, index=pd.RangeIndex(0, 10), name=df.name)

        result_df = empty_obj.agg(self.func, axis=self.axis)

        if isinstance(result_df, pd.DataFrame):
            self.output_types = [OutputType.dataframe]
            return result_df.dtypes, result_df.index
        elif isinstance(result_df, pd.Series):
            self.output_types = [OutputType.series]
            return pd.Series([result_df.dtype], index=[result_df.name]), result_df.index
        else:
            self.output_types = [OutputType.scalar]
            return np.array(result_df).dtype, None