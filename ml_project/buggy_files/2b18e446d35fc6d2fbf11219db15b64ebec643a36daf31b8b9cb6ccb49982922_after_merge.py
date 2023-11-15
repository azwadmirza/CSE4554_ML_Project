    def tile(cls, op: "DataFrameDropNA"):
        in_df = op.inputs[0]
        out_df = op.outputs[0]

        # series tiling will go here
        if len(in_df.chunk_shape) == 1 or in_df.chunk_shape[1] == 1:
            return cls._tile_drop_directly(op)

        subset_df = in_df
        if op.subset:
            subset_df = in_df[op.subset]._inplace_tile()
        count_series = subset_df.agg('count', axis=1, _use_inf_as_na=op.use_inf_as_na)._inplace_tile()

        nsplits, out_shape, left_chunks, right_chunks = align_dataframe_series(in_df, count_series, axis=0)
        out_chunk_indexes = itertools.product(*(range(s) for s in out_shape))

        out_chunks = []
        for out_idx, df_chunk in zip(out_chunk_indexes, left_chunks):
            series_chunk = right_chunks[out_idx[0]]
            kw = dict(shape=(np.nan, nsplits[1][out_idx[1]]), dtypes=df_chunk.dtypes,
                      index_value=df_chunk.index_value, columns_value=df_chunk.columns_value)

            new_op = op.copy().reset_key()
            new_op._drop_directly = False
            new_op._subset_size = len(op.subset) if op.subset else len(in_df.dtypes)
            out_chunks.append(new_op.new_chunk([df_chunk, series_chunk], index=out_idx, **kw))

        new_op = op.copy().reset_key()
        params = out_df.params.copy()
        new_nsplits = list(tuple(ns) for ns in nsplits)
        new_nsplits[0] = (np.nan,) * len(new_nsplits[0])
        params.update(dict(nsplits=tuple(new_nsplits), chunks=out_chunks))
        return new_op.new_tileables(op.inputs, **params)