    def tile_with_mask(cls, op):
        in_df = op.inputs[0]
        out_df = op.outputs[0]

        out_chunks = []

        if isinstance(op.mask, (SERIES_TYPE, DATAFRAME_TYPE, TENSOR_TYPE)):
            mask = op.inputs[1]

            if isinstance(op.mask, SERIES_TYPE):
                nsplits, out_shape, df_chunks, mask_chunks = \
                    align_dataframe_series(in_df, mask, axis='index')
            elif isinstance(op.mask, DATAFRAME_TYPE):
                nsplits, out_shape, df_chunks, mask_chunks = \
                    align_dataframe_dataframe(in_df, mask)
            else:
                # tensor
                nsplits = in_df.nsplits
                mask = mask.rechunk(nsplits[:mask.ndim])._inplace_tile()
                out_shape = in_df.chunk_shape
                df_chunks = in_df.chunks
                mask_chunks = mask.chunks
            out_chunk_indexes = itertools.product(*(range(s) for s in out_shape))

            out_chunks = []
            for i, idx, df_chunk in zip(itertools.count(), out_chunk_indexes, df_chunks):
                if op.mask.ndim == 1:
                    mask_chunk = mask_chunks[df_chunk.index[0]]
                else:
                    mask_chunk = mask_chunks[i]
                index_value = parse_index(out_df.index_value.to_pandas(), df_chunk)
                out_chunk = op.copy().reset_key().new_chunk([df_chunk, mask_chunk], index=idx,
                                                            shape=(np.nan, df_chunk.shape[1]),
                                                            dtypes=df_chunk.dtypes,
                                                            index_value=index_value,
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
                                                   shape=(np.nan, in_chunk.shape[1]),
                                                   dtypes=in_chunk.dtypes,
                                                   index_value=in_df.index_value,
                                                   columns_value=in_chunk.columns_value)
                    out_chunks.append(out_chunk)

        nsplits_on_columns = tuple(c.shape[1] for c in out_chunks if c.index[0] == 0)
        row_chunk_num = len([c.shape[0] for c in out_chunks if c.index[1] == 0])
        nsplits = ((np.nan,) * row_chunk_num, nsplits_on_columns)

        new_op = op.copy()
        return new_op.new_dataframes(op.inputs, shape=out_df.shape, dtypes=out_df.dtypes,
                                     index_value=out_df.index_value, columns_value=out_df.columns_value,
                                     chunks=out_chunks, nsplits=nsplits)