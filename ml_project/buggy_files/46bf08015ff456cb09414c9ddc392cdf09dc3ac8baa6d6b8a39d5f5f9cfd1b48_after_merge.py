    def tile(cls, op):
        in_df = op.inputs[0]
        out_df = op.outputs[0]

        # See Note [Fancy Index of Numpy and Pandas]
        tensor0 = empty(in_df.shape[0], chunk_size=(in_df.nsplits[0],))[op.indexes[0]].tiles()
        tensor1 = empty(in_df.shape[1], chunk_size=(in_df.nsplits[1],))[op.indexes[1]].tiles()

        chunk_mapping = {c0.inputs[0].index + c1.inputs[0].index: (c0, c1)
                         for c0, c1 in itertools.product(tensor0.chunks, tensor1.chunks)}

        out_chunks = []
        for chunk in in_df.chunks:
            if chunk.index not in chunk_mapping:
                out_chunks.append(chunk)
            else:
                chunk_op = op.copy().reset_key()
                index_chunk, column_chunk = chunk_mapping[chunk.index]
                chunk_op._indexes = (index_chunk.op.indexes[0], column_chunk.op.indexes[0])
                chunk_op._value = op.value
                out_chunk = chunk_op.new_chunk([chunk],
                                                shape=chunk.shape, index=chunk.index, dtypes=chunk.dtypes,
                                                index_value=chunk.index_value, columns_value=chunk.columns_value)
                out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_dataframes(op.inputs, shape=out_df.shape, dtypes=out_df.dtypes,
                                     index_value=out_df.index_value, columns_value=out_df.columns_value,
                                     chunks=out_chunks, nsplits=in_df.nsplits)