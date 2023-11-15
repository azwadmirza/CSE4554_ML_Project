    def __call__(self, df, dtypes=None, index=None):
        axis = getattr(self, 'axis', None) or 0
        self._axis = validate_axis(axis, df)

        if self.output_types[0] == OutputType.dataframe:
            dtypes = self._infer_df_func_returns(df.dtypes, dtypes)
        else:
            dtypes = self._infer_df_func_returns((df.name, df.dtype), dtypes)

        for arg, desc in zip((self.output_types, dtypes), ('output_types', 'dtypes')):
            if arg is None:
                raise TypeError(f'Cannot determine {desc} by calculating with enumerate data, '
                                'please specify it as arguments')

        if self.output_types[0] == OutputType.dataframe:
            new_shape = list(df.shape)
            new_index_value = df.index_value
            if len(new_shape) == 1:
                new_shape.append(len(dtypes))
            else:
                new_shape[1] = len(dtypes)

            if self.call_agg:
                new_shape[self.axis] = np.nan
                new_index_value = parse_index(None, (df.key, df.index_value.key))
            return self.new_dataframe([df], shape=tuple(new_shape), dtypes=dtypes, index_value=new_index_value,
                                      columns_value=parse_index(dtypes.index, store_data=True))
        else:
            name, dtype = dtypes

            if isinstance(df, DATAFRAME_TYPE):
                new_shape = (df.shape[1 - axis],)
                new_index_value = [df.columns_value, df.index_value][axis]
            else:
                new_shape = (np.nan,) if self.call_agg else df.shape
                new_index_value = df.index_value

            return self.new_series([df], shape=new_shape, name=name, dtype=dtype, index_value=new_index_value)