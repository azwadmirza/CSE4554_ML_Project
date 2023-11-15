    def tile(cls, op):
        df = op.outputs[0]
        left = build_concatenated_rows_frame(op.inputs[0])
        right = build_concatenated_rows_frame(op.inputs[1])

        # left and right now are guaranteed only chunked along index axis, not column axis.
        if left.chunk_shape[1] > 1:
            check_chunks_unknown_shape([left], TilesError)
            left = left.rechunk({1: left.shape[1]})._inplace_tile()
        if right.chunk_shape[1] > 1:
            check_chunks_unknown_shape([right], TilesError)
            right = right.rechunk({1: right.shape[1]})._inplace_tile()

        if len(left.chunks) == 1 or len(right.chunks) == 1:
            return cls._tile_one_chunk(op, left, right)

        left_row_chunk_size = left.chunk_shape[0]
        right_row_chunk_size = right.chunk_shape[0]
        out_row_chunk_size = max(left_row_chunk_size, right_row_chunk_size)

        out_chunk_shape = (out_row_chunk_size, 1)
        nsplits = [[np.nan for _ in range(out_row_chunk_size)], [df.shape[1]]]

        left_on = _prepare_shuffle_on(op.left_index, op.left_on, op.on)
        right_on = _prepare_shuffle_on(op.right_index, op.right_on, op.on)

        # do shuffle
        left_chunks = cls._gen_shuffle_chunks(op, out_chunk_shape, left_on, left)
        right_chunks = cls._gen_shuffle_chunks(op, out_chunk_shape, right_on, right)

        out_chunks = []
        for left_chunk, right_chunk in zip(left_chunks, right_chunks):
            merge_op = op.copy().reset_key()
            out_chunk = merge_op.new_chunk([left_chunk, right_chunk], shape=(np.nan, df.shape[1]),
                                           index=left_chunk.index,
                                           index_value=infer_index_value(left_chunk.index_value,
                                                                         right_chunk.index_value),
                                           columns_value=df.columns_value)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_dataframes(op.inputs, df.shape,
                                     nsplits=tuple(tuple(ns) for ns in nsplits),
                                     chunks=out_chunks, dtypes=df.dtypes,
                                     index_value=df.index_value, columns_value=df.columns_value)