    def _tile_dataframe_series(cls, op):
        left, right = op.lhs, op.rhs
        df = op.outputs[0]

        nsplits, out_shape, left_chunks, right_chunks = align_dataframe_series(left, right, axis=op.axis)
        out_chunk_indexes = itertools.product(*(range(s) for s in out_shape))

        out_chunks = []
        for out_idx, df_chunk in zip(out_chunk_indexes, left_chunks):
            if op.axis == 'columns' or op.axis == 1:
                series_chunk = right_chunks[out_idx[1]]
                kw = {
                    'shape': (df_chunk.shape[0], np.nan),
                    'index_value': df_chunk.index_value,
                }
            else:
                series_chunk = right_chunks[out_idx[0]]
                kw = {
                    'shape': (np.nan, df_chunk.shape[1]),
                    'columns_value': df_chunk.columns,
                }
            out_chunk = op.copy().reset_key().new_chunk([df_chunk, series_chunk], index=out_idx, **kw)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_dataframes(op.inputs, df.shape,
                                     nsplits=tuple(tuple(ns) for ns in nsplits),
                                     chunks=out_chunks, dtypes=df.dtypes,
                                     index_value=df.index_value, columns_value=df.columns)