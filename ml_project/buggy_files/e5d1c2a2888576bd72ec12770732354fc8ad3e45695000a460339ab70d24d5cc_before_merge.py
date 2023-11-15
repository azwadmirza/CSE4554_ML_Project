    def tile(cls, op):
        out_df = op.outputs[0]
        in_tensor = op.input
        out_chunks = []
        nsplits = in_tensor.nsplits
        if any(any(np.isnan(ns)) for ns in nsplits):
            raise NotImplementedError('NAN shape is not supported in DataFrame')

        cum_size = [np.cumsum(s) for s in nsplits]
        for in_chunk in in_tensor.chunks:
            out_op = op.copy().reset_key()
            if in_chunk.ndim == 1:
                i, = in_chunk.index
                column_stop = 1
                index = (in_chunk.index[0], 0)
                columns_value = parse_index(out_df.columns.to_pandas()[0:1], store_data=True)
            else:
                i, j = in_chunk.index
                column_stop = cum_size[1][j]
                index = in_chunk.index
                columns_value = parse_index(out_df.columns.to_pandas()[column_stop - in_chunk.shape[1]:column_stop],
                                            store_data=True)

            index_stop = cum_size[0][i]
            if out_df.index_value is not None:
                index_value = parse_index(out_df.index_value.to_pandas()[index_stop - in_chunk.shape[0]:index_stop],
                                          store_data=True)
            else:
                index_value = parse_index(pd.RangeIndex(start=index_stop - in_chunk.shape[0], stop=index_stop))

            out_op.extra_params['index_stop'] = index_stop
            out_op.extra_params['column_stop'] = column_stop
            out_chunk = out_op.new_chunk([in_chunk], shape=in_chunk.shape, index=index,
                                         index_value=index_value, columns_value=columns_value)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_dataframes(out_df.inputs, out_df.shape, dtypes=out_df.dtypes,
                                     index_value=out_df.index_value,
                                     columns_value=out_df.columns,
                                     chunks=out_chunks, nsplits=in_tensor.nsplits)