    def _create_chunk(self, output_idx, index, **kw):
        inputs = self.inputs
        if kw.get('index_value', None) is None and inputs[0].index_value is not None:
            input_index_value = inputs[0].index_value
            index_min_max = self.index_min_max
            if index_min_max is not None:
                kw['index_value'] = filter_index_value(input_index_value, index_min_max)
            else:
                kw['index_value'] = parse_index(inputs[0].index_value.to_pandas(),
                                                key=tokenize(input_index_value.key,
                                                             type(self).__name__))
        if kw.get('columns_value', None) is None and getattr(inputs[0], 'columns_value', None) is not None:
            input_columns_value = inputs[0].columns_value
            input_dtypes = inputs[0].dtypes
            column_min_max = self.column_min_max
            if column_min_max is not None:
                kw['columns_value'] = filter_index_value(input_columns_value, column_min_max,
                                                         store_data=True)
            else:
                kw['columns_value'] = parse_index(inputs[0].columns_value.to_pandas(),
                                                  key=tokenize(input_columns_value.key,
                                                               type(self).__name__))
            kw['dtypes'] = input_dtypes[kw['columns_value'].to_pandas()]
            column_shuffle_size = self.column_shuffle_size
            if column_shuffle_size is not None:
                self._column_shuffle_segments = hash_dtypes(input_dtypes, column_shuffle_size)
        if kw.get('dtype', None) and getattr(inputs[0], 'dtype', None) is not None:
            kw['dtype'] = inputs[0].dtype
        if kw.get('name', None) and getattr(inputs[0], 'name', None) is not None:
            kw['name'] = inputs[0].dtype
        return super(DataFrameIndexAlignMap, self)._create_chunk(output_idx, index, **kw)