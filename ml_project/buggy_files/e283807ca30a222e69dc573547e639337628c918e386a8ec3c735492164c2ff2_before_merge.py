    def tile_with_mask(cls, op):
        in_df = op.inputs[0]
        out_df = op.outputs[0]

        out_chunks = []

        if isinstance(op.mask, SERIES_TYPE):
            mask = op.inputs[1]

            nsplits, out_shape, df_chunks, mask_chunks = align_dataframe_series(in_df, mask, axis='index')
            out_chunk_indexes = itertools.product(*(range(s) for s in out_shape))

            out_chunks = []
            for idx, df_chunk in zip(out_chunk_indexes, df_chunks):
                mask_chunk = mask_chunks[df_chunk.index[0]]
                out_chunk = op.copy().reset_key().new_chunk([df_chunk, mask_chunk],
                                                            shape=(np.nan, df_chunk.shape[1]), index=idx,
                                                            index_value=df_chunk.index_value,
                                                            columns_value=df_chunk.columns_value)
                out_chunks.append(out_chunk)

        else:
            check_chunks_unknown_shape([in_df], TilesError)
            nsplits_acc = np.cumsum((0,) + in_df.nsplits[0])
            for idx in range(in_df.chunk_shape[0]):
                for idxj in range(in_df.chunk_shape[1]):
                    in_chunk = in_df.cix[idx, idxj]
                    chunk_op = op.copy().reset_key()
                    chunk_op._mask = op.mask.iloc[nsplits_acc[idx]:nsplits_acc[idx+1]]
                    out_chunk = chunk_op.new_chunk([in_chunk], index=in_chunk.index,
                                                   shape=(np.nan, in_chunk.shape[1]), dtypes=in_chunk.dtypes,
                                                   index_value=in_df.index_value, columns_value=in_chunk.columns_value)
                    out_chunks.append(out_chunk)

            nsplits = ((np.nan,) * in_df.chunk_shape[0], in_df.nsplits[1])

        new_op = op.copy()
        return new_op.new_dataframes(op.inputs, shape=out_df.shape, dtypes=out_df.dtypes,
                                     index_value=out_df.index_value, columns_value=out_df.columns_value,
                                     chunks=out_chunks, nsplits=nsplits)