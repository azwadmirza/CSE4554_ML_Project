    def tile(cls, op: "DataFrameCartesianChunk"):
        left = op.left
        right = op.right
        out = op.outputs[0]

        if left.ndim == 2 and left.chunk_shape[1] > 1:
            check_chunks_unknown_shape([left], TilesError)
            # if left is a DataFrame, make sure 1 chunk on axis columns
            left = left.rechunk({1: left.shape[1]})._inplace_tile()
        if right.ndim == 2 and right.chunk_shape[1] > 1:
            check_chunks_unknown_shape([right], TilesError)
            # if right is a DataFrame, make sure 1 chunk on axis columns
            right = right.rechunk({1: right.shape[1]})._inplace_tile()

        out_chunks = []
        nsplits = [[]] if out.ndim == 1 else [[], [out.shape[1]]]
        i = 0
        for left_chunk in left.chunks:
            for right_chunk in right.chunks:
                chunk_op = op.copy().reset_key()
                chunk_op._tileable_op_key = op.key
                if op.output_types[0] == OutputType.dataframe:
                    shape = (np.nan, out.shape[1])
                    index_value = parse_index(out.index_value.to_pandas(),
                                              left_chunk, right_chunk,
                                              op.func, op.args, op.kwargs)
                    out_chunk = chunk_op.new_chunk([left_chunk, right_chunk],
                                                   shape=shape,
                                                   index_value=index_value,
                                                   columns_value=out.columns_value,
                                                   dtypes=out.dtypes,
                                                   index=(i, 0))
                    out_chunks.append(out_chunk)
                    nsplits[0].append(out_chunk.shape[0])
                else:
                    shape = (np.nan,)
                    index_value = parse_index(out.index_value.to_pandas(),
                                              left_chunk, right_chunk,
                                              op.func, op.args, op.kwargs)
                    out_chunk = chunk_op.new_chunk([left_chunk, right_chunk],
                                                   shape=shape,
                                                   index_value=index_value,
                                                   dtype=out.dtype,
                                                   name=out.name,
                                                   index=(i,))
                    out_chunks.append(out_chunk)
                    nsplits[0].append(out_chunk.shape[0])
                i += 1

        params = out.params
        params['nsplits'] = tuple(tuple(ns) for ns in nsplits)
        params['chunks'] = out_chunks
        new_op = op.copy()
        return new_op.new_tileables(op.inputs, kws=[params])