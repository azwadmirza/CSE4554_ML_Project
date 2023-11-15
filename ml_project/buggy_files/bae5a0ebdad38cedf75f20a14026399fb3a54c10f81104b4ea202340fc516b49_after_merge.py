    def tile(cls, op):
        in_df = op.inputs[0]
        out_df = op.outputs[0]

        if not isinstance(op.keys, six.string_types):
            raise NotImplementedError('DataFrame.set_index only support label')
        if op.verify_integrity:
            raise NotImplementedError('DataFrame.set_index not support verify_integrity yet')

        out_chunks = []

        try:
            column_index = in_df.columns_value.to_pandas().get_loc(op.keys)
        except KeyError:
            raise NotImplementedError('The new index label must be a column of the original dataframe')

        chunk_index = np.searchsorted(np.cumsum(in_df.nsplits[1]), column_index + 1)

        for row_idx in range(in_df.chunk_shape[0]):
            index_chunk = in_df.cix[row_idx, chunk_index]
            for col_idx in range(in_df.chunk_shape[1]):
                input_chunk = in_df.cix[row_idx, col_idx]
                if op.drop and input_chunk.key == index_chunk.key:
                    new_shape = (input_chunk.shape[0], input_chunk.shape[1] - 1)
                    columns = parse_index(input_chunk.columns_value.to_pandas().drop(op.keys), store_data=True)
                else:
                    new_shape = input_chunk.shape
                    columns = input_chunk.columns_value
                out_op = op.copy().reset_key()
                out_chunk = out_op.new_chunk([index_chunk, input_chunk],
                                             shape=new_shape, dtypes=out_df.dtypes, index=input_chunk.index,
                                             index_value=parse_index(pd.Int64Index([])),
                                             columns_value=columns)
                out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_dataframes(op.inputs, out_df.shape, dtypes=out_df.dtypes,
                                     index_value=out_df.index_value,
                                     columns_value=out_df.columns_value,
                                     chunks=out_chunks, nsplits=in_df.nsplits)