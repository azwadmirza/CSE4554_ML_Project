    def _tile_input_tensor(cls, op):
        out_df = op.outputs[0]
        in_tensor = op.input
        out_chunks = []
        nsplits = in_tensor.nsplits

        if op.index is not None:
            # rechunk index if it's a tensor
            check_chunks_unknown_shape(op.inputs, TilesError)
            index_tensor = op.index.rechunk([nsplits[0]])._inplace_tile()
        else:
            index_tensor = None

        cum_size = [np.cumsum(s) for s in nsplits]
        for in_chunk in in_tensor.chunks:
            out_op = op.copy().reset_key()
            chunk_inputs = [in_chunk]
            if in_chunk.ndim == 1:
                i, = in_chunk.index
                column_stop = 1
                chunk_index = (in_chunk.index[0], 0)
                dtypes = out_df.dtypes
                columns_value = parse_index(out_df.columns_value.to_pandas()[0:1],
                                            store_data=True)
                chunk_shape = (in_chunk.shape[0], 1)
            else:
                i, j = in_chunk.index
                column_stop = cum_size[1][j]
                chunk_index = in_chunk.index
                dtypes = out_df.dtypes[column_stop - in_chunk.shape[1]:column_stop]
                pd_columns = out_df.columns_value.to_pandas()
                chunk_pd_columns = pd_columns[column_stop - in_chunk.shape[1]:column_stop]
                columns_value = parse_index(chunk_pd_columns, store_data=True)
                chunk_shape = in_chunk.shape

            index_stop = cum_size[0][i]
            if isinstance(op.index, INDEX_TYPE):
                index_chunk = index_tensor.chunks[i]
                index_value = index_chunk.index_value
                chunk_inputs.append(index_chunk)
            elif isinstance(in_chunk, SERIES_CHUNK_TYPE):
                index_value = in_chunk.index_value
            elif out_df.index_value.has_value():
                pd_index = out_df.index_value.to_pandas()
                chunk_pd_index = pd_index[index_stop - in_chunk.shape[0]:index_stop]
                index_value = parse_index(chunk_pd_index, store_data=True)
            elif op.index is None:
                # input tensor has unknown shape
                index_value = parse_index(pd.RangeIndex(-1), in_chunk)
            else:
                index_chunk = index_tensor.cix[in_chunk.index[0], ]
                chunk_inputs.append(index_chunk)
                index_value = parse_index(pd.Index([], dtype=index_tensor.dtype),
                                          index_chunk, type(out_op).__name__)

            out_op.extra_params['index_stop'] = index_stop
            out_op.extra_params['column_stop'] = column_stop
            out_chunk = out_op.new_chunk(chunk_inputs, shape=chunk_shape,
                                         index=chunk_index, dtypes=dtypes,
                                         index_value=index_value,
                                         columns_value=columns_value)
            out_chunks.append(out_chunk)

        if in_tensor.ndim == 1:
            nsplits = in_tensor.nsplits + ((1,),)
        else:
            nsplits = in_tensor.nsplits

        new_op = op.copy()
        return new_op.new_dataframes(out_df.inputs, out_df.shape, dtypes=out_df.dtypes,
                                     index_value=out_df.index_value, columns_value=out_df.columns_value,
                                     chunks=out_chunks, nsplits=nsplits)