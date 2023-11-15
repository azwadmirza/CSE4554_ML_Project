    def _calc_result_shape(self, df):
        if self.output_types[0] == OutputType.dataframe:
            test_obj = build_df(df, size=10)
        else:
            test_obj = build_series(df, size=10, name=df.name)

        result_df = test_obj.agg(self.func, axis=self.axis)

        if isinstance(result_df, pd.DataFrame):
            self.output_types = [OutputType.dataframe]
            return result_df.dtypes, result_df.index
        elif isinstance(result_df, pd.Series):
            self.output_types = [OutputType.series]
            return pd.Series([result_df.dtype], index=[result_df.name]), result_df.index
        else:
            self.output_types = [OutputType.scalar]
            return np.array(result_df).dtype, None