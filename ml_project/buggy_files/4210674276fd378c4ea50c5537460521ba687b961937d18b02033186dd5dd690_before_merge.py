    def _tile_scalar(cls, op):
        tileable = op.rhs if np.isscalar(op.lhs) else op.lhs
        df = op.outputs[0]
        out_chunks = []
        for chunk in tileable.chunks:
            out_op = op.copy().reset_key()
            if isinstance(chunk, DATAFRAME_CHUNK_TYPE):
                out_chunk = out_op.new_chunk([chunk], shape=chunk.shape, index=chunk.index, dtypes=chunk.dtypes,
                                            index_value=chunk.index_value, columns_value=getattr(chunk, 'columns'))
            else:
                out_chunk = out_op.new_chunk([chunk], shape=chunk.shape, index=chunk.index, dtype=chunk.dtype,
                                            index_value=chunk.index_value, name=getattr(chunk, 'name'))
            out_chunks.append(out_chunk)

        new_op = op.copy()
        if isinstance(df, SERIES_TYPE):
            return new_op.new_seriess(op.inputs, df.shape, nsplits=tileable.nsplits, dtype=df.dtype,
                                      index_value=df.index_value, name=df.name, chunks=out_chunks)
        else:
            return new_op.new_dataframes(op.inputs, df.shape, nsplits=tileable.nsplits, dtypes=df.dtypes,
                                         index_value=df.index_value, columns_value=df.columns, chunks=out_chunks)