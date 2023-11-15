    def tile(cls, op):
        in_df = build_concated_rows_frame(op.inputs[0])
        out_df = op.outputs[0]

        # First, perform groupby and aggregation on each chunk.
        agg_chunks = []
        for chunk in in_df.chunks:
            agg_op = op.copy().reset_key()
            agg_op._stage = Stage.agg
            agg_chunk = agg_op.new_chunk([chunk], shape=out_df.shape, index=chunk.index,
                                         index_value=out_df.index_value,
                                         columns_value=out_df.columns_value)
            agg_chunks.append(agg_chunk)

        # Shuffle the aggregation chunk.
        reduce_chunks = cls._gen_shuffle_chunks(op, in_df, agg_chunks)

        # Combine groups
        combine_chunks = []
        for chunk in reduce_chunks:
            combine_op = op.copy().reset_key()
            combine_op._stage = Stage.combine
            combine_chunk = combine_op.new_chunk([chunk], shape=out_df.shape, index=chunk.index,
                                                 index_value=out_df.index_value,
                                                 columns_value=out_df.columns_value)
            combine_chunks.append(combine_chunk)

        new_op = op.copy()
        return new_op.new_dataframes([in_df], shape=out_df.shape, index_value=out_df.index_value,
                                     columns_value=out_df.columns_value, chunks=combine_chunks,
                                     nsplits=((np.nan,) * len(combine_chunks), (out_df.shape[1],)))