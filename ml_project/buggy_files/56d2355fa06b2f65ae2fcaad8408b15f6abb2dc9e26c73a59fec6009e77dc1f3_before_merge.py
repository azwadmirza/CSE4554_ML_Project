    def tile(cls, op):
        in_df = op.inputs[0]
        out_val = op.outputs[0]

        # See Note [Fancy Index of Numpy and Pandas]
        tensor0 = empty(in_df.shape[0], chunk_size=(in_df.nsplits[0],))[op.indexes[0]].tiles()
        tensor1 = empty(in_df.shape[1], chunk_size=(in_df.nsplits[1],))[op.indexes[1]].tiles()

        integral_index_on_index = isinstance(op.indexes[0], Integral)
        integral_index_on_column = isinstance(op.indexes[1], Integral)

        out_chunks = []
        for index_chunk, column_chunk in itertools.product(tensor0.chunks, tensor1.chunks):
            in_chunk = in_df.cix[index_chunk.inputs[0].index + column_chunk.inputs[0].index]

            chunk_op = op.copy().reset_key()
            chunk_op._indexes = (index_chunk.op.indexes[0], column_chunk.op.indexes[0])

            if integral_index_on_column:
                shape = index_chunk.shape
                index = index_chunk.index
                index_value = indexing_index_value(in_chunk.index_value, index_chunk.op.indexes[0])
                out_chunk = chunk_op.new_chunk([in_chunk], shape=shape, index=index,
                                               dtype=out_val.dtype, index_value=index_value)
            elif integral_index_on_index:
                shape = column_chunk.shape
                index = column_chunk.index
                index_value = indexing_index_value(in_chunk.columns, column_chunk.op.indexes[0])
                out_chunk = chunk_op.new_chunk([in_chunk], shape=shape, index=index,
                                               dtype=out_val.dtype, index_value=index_value)
            else:
                index_value = indexing_index_value(in_chunk.index_value, index_chunk.op.indexes[0])
                columns_value = indexing_index_value(in_chunk.columns, column_chunk.op.indexes[0], store_data=True)
                dtypes = in_chunk.dtypes.iloc[column_chunk.op.indexes[0]]
                out_chunk = chunk_op.new_chunk([in_chunk],
                                               shape=index_chunk.shape + column_chunk.shape,
                                               index=index_chunk.index + column_chunk.index,
                                               dtypes=dtypes, index_value=index_value, columns_value=columns_value)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        if integral_index_on_column or integral_index_on_index:
            if integral_index_on_column:
                nsplits = tensor0.nsplits
            else:
                nsplits = tensor1.nsplits
            return new_op.new_seriess(op.inputs, out_val.shape, dtype=out_val.dtype,
                                      index_value=out_val.index_value, chunks=out_chunks, nsplits=nsplits)
        else:
            nsplits = tensor0.nsplits + tensor1.nsplits
            return new_op.new_dataframes(op.inputs, out_val.shape, dtypes=out_val.dtypes,
                                        index_value=out_val.index_value,
                                        columns_value=out_val.columns, chunks=out_chunks, nsplits=nsplits)