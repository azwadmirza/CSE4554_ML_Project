    def _create_chunk(self, output_idx, index, **kw):
        inputs = self.inputs
        if kw.get('index_value', None) is None and inputs[0].inputs[0].index_value is not None:
            index_align_map_chunks = inputs[0].inputs
            if index_align_map_chunks[0].op.index_min_max is not None:
                # shuffle on columns, all the DataFrameIndexAlignMap has the same index
                kw['index_value'] = filter_index_value(index_align_map_chunks[0].index_value,
                                                       index_align_map_chunks[0].op.index_min_max)
            else:
                # shuffle on index
                kw['index_value'] = parse_index(index_align_map_chunks[0].index_value.to_pandas(),
                                                key=tokenize([c.key for c in index_align_map_chunks],
                                                             type(self).__name__))
        if kw.get('columns_value', None) is None and getattr(inputs[0].inputs[0], 'columns_value', None) is not None:
            index_align_map_chunks = inputs[0].inputs
            if index_align_map_chunks[0].op.column_min_max is not None:
                # shuffle on index
                kw['columns_value'] = filter_index_value(index_align_map_chunks[0].columns_value,
                                                         index_align_map_chunks[0].op.column_min_max,
                                                         store_data=True)
                kw['dtypes'] = index_align_map_chunks[0].dtypes[kw['columns_value'].to_pandas()]
            else:
                # shuffle on columns
                all_dtypes = [c.op.column_shuffle_segments[index[1]] for c in index_align_map_chunks
                              if c.index[0] == index_align_map_chunks[0].index[0]]
                kw['dtypes'] = pd.concat(all_dtypes)
                kw['columns_value'] = parse_index(kw['dtypes'].index, store_data=True)
        if kw.get('dtype', None) and getattr(inputs[0].inputs[0], 'dtype', None) is not None:
            kw['dtype'] = inputs[0].inputs[0].dtype
        if kw.get('name', None) and getattr(inputs[0].inputs[0], 'name', None) is not None:
            kw['name'] = inputs[0].inputs[0].dtype
        return super(DataFrameIndexAlignReduce, self)._create_chunk(output_idx, index, **kw)