    def _call_dataframe(self, df, dtypes=None, index=None):
        dtypes, index_value = self._infer_df_func_returns(df, dtypes, index)
        for arg, desc in zip((self.output_types, dtypes, index_value),
                             ('output_types', 'dtypes', 'index')):
            if arg is None:
                raise TypeError(f'Cannot determine {desc} by calculating with enumerate data, '
                                'please specify it as arguments')

        if index_value == 'inherit':
            index_value = df.index_value

        if self._elementwise:
            shape = df.shape
        elif self.output_types[0] == OutputType.dataframe:
            shape = [np.nan, np.nan]
            shape[1 - self.axis] = df.shape[1 - self.axis]
            shape = tuple(shape)
        else:
            shape = (df.shape[1 - self.axis],)

        if self.output_types[0] == OutputType.dataframe:
            if self.axis == 0:
                return self.new_dataframe([df], shape=shape, dtypes=dtypes, index_value=index_value,
                                          columns_value=parse_index(dtypes.index))
            else:
                return self.new_dataframe([df], shape=shape, dtypes=dtypes, index_value=df.index_value,
                                          columns_value=parse_index(dtypes.index))
        else:
            return self.new_series([df], shape=shape, dtype=dtypes, index_value=index_value)