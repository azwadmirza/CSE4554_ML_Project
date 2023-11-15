    def _tile_series_dataframe(cls, op):
        left, right = op.lhs, op.rhs
        df = op.outputs[0]

        nsplits, out_shape, right_chunks, left_chunks = align_dataframe_series(right, left, axis=op.axis)
        out_chunk_indexes = itertools.product(*(range(s) for s in out_shape))

        out_chunks = []
        for out_idx, df_chunk in zip(out_chunk_indexes, right_chunks):
            if op.axis == 'columns' or op.axis == 1:
                series_chunk = left_chunks[out_idx[1]]
                kw = {
                    'shape': (df_chunk.shape[0], np.nan),
                    'index_value': df_chunk.index_value,
                }
            else:
                series_chunk = left_chunks[out_idx[0]]
                kw = {
                    'shape': (df_chunk.shape[0], np.nan),
                    'index_value': df_chunk.index_value,
                }
            out_chunk = op.copy().reset_key().new_chunk([series_chunk, df_chunk], index=out_idx, **kw)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_dataframes(op.inputs, df.shape,
                                     nsplits=tuple(tuple(ns) for ns in nsplits),
                                     chunks=out_chunks, dtypes=df.dtypes,
                                     index_value=df.index_value, columns_value=df.columns)