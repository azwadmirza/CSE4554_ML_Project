    def _tile_dataframe(cls, op):
        in_df = op.inputs[0]
        out_df = op.outputs[0]
        added_columns_num = len(out_df.dtypes) - len(in_df.dtypes)
        out_chunks = []
        index_has_value = out_df.index_value.has_value()
        chunk_has_nan = any(np.isnan(s) for s in in_df.nsplits[0])
        cum_range = np.cumsum((0, ) + in_df.nsplits[0])
        for c in in_df.chunks:
            if index_has_value:
                if chunk_has_nan:
                    index_value = parse_index(pd.RangeIndex(-1))
                else:
                    index_value = parse_index(pd.RangeIndex(cum_range[c.index[0]], cum_range[c.index[0] + 1]))
            else:
                index_value = out_df.index_value
            if c.index[1] == 0:
                chunk_op = op.copy().reset_key()
                dtypes = out_df.dtypes[:(added_columns_num + len(c.dtypes))]
                columns_value = parse_index(dtypes.index)
                new_chunk = chunk_op.new_chunk([c], shape=(c.shape[0], c.shape[1] + added_columns_num),
                                               index=c.index, index_value=index_value,
                                               columns_value=columns_value, dtypes=dtypes)
            else:
                chunk_op = op.copy().reset_key()
                chunk_op._drop = True
                new_chunk = chunk_op.new_chunk([c], shape=c.shape, index_value=index_value,
                                               index=c.index, columns_value=c.columns_value, dtypes=c.dtypes)
            out_chunks.append(new_chunk)
        if not index_has_value or chunk_has_nan:
            if isinstance(out_df.index_value._index_value, IndexValue.RangeIndex):
                out_chunks = standardize_range_index(out_chunks)
        new_op = op.copy()
        columns_splits = list(in_df.nsplits[1])
        columns_splits[0] += added_columns_num
        nsplits = (in_df.nsplits[0], tuple(columns_splits))
        return new_op.new_dataframes(op.inputs, out_df.shape, nsplits=nsplits,
                                     chunks=out_chunks, dtypes=out_df.dtypes,
                                     index_value=out_df.index_value, columns_value=out_df.columns_value)