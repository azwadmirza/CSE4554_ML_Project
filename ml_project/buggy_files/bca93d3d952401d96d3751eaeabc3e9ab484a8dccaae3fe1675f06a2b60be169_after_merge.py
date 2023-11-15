    def _calc_properties(cls, x1, x2=None, axis='columns'):
        if isinstance(x1, (DATAFRAME_TYPE, DATAFRAME_CHUNK_TYPE)) and (x2 is None or np.isscalar(x2)):
            # FIXME infer the dtypes of result df properly
            return {'shape': x1.shape, 'dtypes': x1.dtypes,
                    'columns_value': x1.columns_value, 'index_value': x1.index_value}

        if isinstance(x1, (SERIES_TYPE, SERIES_CHUNK_TYPE)) and (x2 is None or np.isscalar(x2)):
            dtype = find_common_type([x1.dtype, type(x2)])
            return {'shape': x1.shape, 'dtype': dtype, 'index_value': x1.index_value}

        if isinstance(x1, (DATAFRAME_TYPE, DATAFRAME_CHUNK_TYPE)) and isinstance(
                x2, (DATAFRAME_TYPE, DATAFRAME_CHUNK_TYPE)):
            index_shape, column_shape, dtypes, columns, index = np.nan, np.nan, None, None, None

            if x1.columns_value is not None and x2.columns_value is not None and \
                    x1.columns_value.key == x2.columns_value.key:
                dtypes = x1.dtypes
                columns = copy.copy(x1.columns_value)
                columns.value.should_be_monotonic = False
                column_shape = len(dtypes)
            elif x1.dtypes is not None and x2.dtypes is not None:
                dtypes = infer_dtypes(x1.dtypes, x2.dtypes, cls._operator)
                columns = parse_index(dtypes.index, store_data=True)
                columns.value.should_be_monotonic = True
                column_shape = len(dtypes)
            if x1.index_value is not None and x2.index_value is not None:
                if x1.index_value.key == x2.index_value.key:
                    index = copy.copy(x1.index_value)
                    index.value.should_be_monotonic = False
                    index_shape = x1.shape[0]
                else:
                    index = infer_index_value(x1.index_value, x2.index_value)
                    index.value.should_be_monotonic = True
                    if index.key == x1.index_value.key == x2.index_value.key and \
                            (not np.isnan(x1.shape[0]) or not np.isnan(x2.shape[0])):
                        index_shape = x1.shape[0] if not np.isnan(x1.shape[0]) else x2.shape[0]

            return {'shape': (index_shape, column_shape), 'dtypes': dtypes,
                    'columns_value': columns, 'index_value': index}

        if isinstance(x1, (DATAFRAME_TYPE, DATAFRAME_CHUNK_TYPE)) and isinstance(x2, (SERIES_TYPE, SERIES_CHUNK_TYPE)):
            if axis == 'columns' or axis == 1:
                index_shape = x1.shape[0]
                index = x1.index_value
                column_shape, dtypes, columns = np.nan, None, None
                if x1.columns_value is not None and x1.index_value is not None:
                    if x1.columns_value.key == x2.index_value.key:
                        dtypes = x1.dtypes
                        columns = copy.copy(x1.columns_value)
                        columns.value.should_be_monotonic = False
                        column_shape = len(dtypes)
                    else:
                        dtypes = x1.dtypes  # FIXME
                        columns = infer_index_value(x1.columns_value, x2.index_value)
                        columns.value.should_be_monotonic = True
                        column_shape = np.nan
            else:
                assert axis == 'index' or axis == 0
                column_shape = x1.shape[1]
                columns = x1.columns_value
                dtypes = x1.dtypes
                index_shape, index = np.nan, None
                if x1.index_value is not None and x1.index_value is not None:
                    if x1.index_value.key == x2.index_value.key:
                        index = copy.copy(x1.columns_value)
                        index.value.should_be_monotonic = False
                        index_shape = x1.shape[0]
                    else:
                        index = infer_index_value(x1.index_value, x2.index_value)
                        index.value.should_be_monotonic = True
                        index_shape = np.nan
            return {'shape': (index_shape, column_shape), 'dtypes': dtypes,
                    'columns_value': columns, 'index_value': index}

        if isinstance(x1, (SERIES_TYPE, SERIES_CHUNK_TYPE)) and isinstance(x2, (SERIES_TYPE, SERIES_CHUNK_TYPE)):
            index_shape, dtype, index = np.nan, None, None

            dtype = find_common_type([x1.dtype, x2.dtype])
            if x1.index_value is not None and x2.index_value is not None:
                if x1.index_value.key == x2.index_value.key:
                    index = copy.copy(x1.index_value)
                    index.value.should_be_monotonic = False
                    index_shape = x1.shape[0]
                else:
                    index = infer_index_value(x1.index_value, x2.index_value)
                    index.value.should_be_monotonic = True
                    if index.key == x1.index_value.key == x2.index_value.key and \
                            (not np.isnan(x1.shape[0]) or not np.isnan(x2.shape[0])):
                        index_shape = x1.shape[0] if not np.isnan(x1.shape[0]) else x2.shape[0]

            return {'shape': (index_shape,), 'dtype': dtype, 'index_value': index}

        raise NotImplementedError('Unknown combination of parameters')