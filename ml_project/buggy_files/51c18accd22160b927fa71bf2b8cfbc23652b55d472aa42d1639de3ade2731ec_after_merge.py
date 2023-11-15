    def __call__(self, expanding):
        inp = expanding.input
        raw_func = self.func
        self._normalize_funcs()

        if isinstance(inp, DATAFRAME_TYPE):
            empty_df = build_df(inp)
            for c, t in empty_df.dtypes.items():
                if t == np.dtype('O'):
                    empty_df[c] = 'O'

            test_df = expanding(empty_df).agg(raw_func)
            if self._axis == 0:
                index_value = inp.index_value
            else:
                index_value = parse_index(test_df.index,
                                          expanding.params, inp,
                                          store_data=False)
            self._append_index = test_df.columns.nlevels != empty_df.columns.nlevels
            return self.new_dataframe(
                [inp], shape=(inp.shape[0], test_df.shape[1]),
                dtypes=test_df.dtypes, index_value=index_value,
                columns_value=parse_index(test_df.columns, store_data=True))
        else:
            pd_index = inp.index_value.to_pandas()
            empty_series = build_empty_series(inp.dtype, index=pd_index[:0], name=inp.name)
            test_obj = expanding(empty_series).agg(raw_func)
            if isinstance(test_obj, pd.DataFrame):
                return self.new_dataframe([inp], shape=(inp.shape[0], test_obj.shape[1]),
                                          dtypes=test_obj.dtypes, index_value=inp.index_value,
                                          columns_value=parse_index(test_obj.dtypes.index, store_data=True))
            else:
                return self.new_series([inp], shape=inp.shape, dtype=test_obj.dtype,
                                       index_value=inp.index_value, name=test_obj.name)