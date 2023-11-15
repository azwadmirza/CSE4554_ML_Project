    def _calc_properties(cls, x1, x2):
        dtypes = columns = index = None
        index_shape = column_shape = np.nan

        if x1.columns.key == x2.columns.key:
            dtypes = x1.dtypes
            column_shape = len(dtypes)
            columns = copy.copy(x1.columns)
            columns.value.should_be_monotonic = True
        elif x1.dtypes is not None and x2.dtypes is not None:
            dtypes = infer_dtypes(x1.dtypes, x2.dtypes, cls._operator)
            column_shape = len(dtypes)
            columns = parse_index(dtypes.index, store_data=True)
            columns.value.should_be_monotonic = True

        if x1.index_value.key == x2.index_value.key:
            index = copy.copy(x1.index_value)
            index.value.should_be_monotonic = True
            index_shape = x1.shape[0]
        elif x1.index_value is not None and x2.index_value is not None:
            index = infer_index_value(x1.index_value, x2.index_value, cls._operator)
            index.value.should_be_monotonic = True
            if index.key == x1.index_value.key == x2.index_value.key and \
                    (not np.isnan(x1.shape[0]) or not np.isnan(x2.shape[0])):
                index_shape = x1.shape[0] if not np.isnan(x1.shape[0]) else x2.shape[0]

        return {'shape': (index_shape, column_shape), 'dtypes': dtypes,
                'columns_value': columns, 'index_value': index}