    def _tile_dataframe(cls, op):
        from ..indexing.iloc import DataFrameIlocGetItem

        out_df = op.outputs[0]
        inputs = op.inputs

        check_chunks_unknown_shape(inputs, TilesError)

        normalized_nsplits = {1: inputs[0].nsplits[1]} if op.axis == 0 else {0: inputs[0].nsplits[0]}
        inputs = [item.rechunk(normalized_nsplits)._inplace_tile() for item in inputs]
        out_chunks = []
        nsplits = []
        cum_index = 0
        for df in inputs:
            for c in df.chunks:
                if op.axis == 0:
                    index = (c.index[0] + cum_index, c.index[1])
                else:
                    index = (c.index[0], c.index[1] + cum_index)

                iloc_op = DataFrameIlocGetItem(indexes=(slice(None),) * 2)
                out_chunks.append(iloc_op.new_chunk([c], shape=c.shape, index=index,
                                                    dtypes=c.dtypes,
                                                    index_value=c.index_value,
                                                    columns_value=c.columns_value))
            nsplits.extend(df.nsplits[op.axis])
            cum_index += len(df.nsplits[op.axis])
        out_nsplits = (tuple(nsplits), inputs[0].nsplits[1]) \
            if op.axis == 0 else (inputs[0].nsplits[0], tuple(nsplits))

        if op.ignore_index:
            out_chunks = standardize_range_index(out_chunks)

        new_op = op.copy()
        return new_op.new_dataframes(op.inputs, out_df.shape,
                                     nsplits=out_nsplits, chunks=out_chunks,
                                     dtypes=out_df.dtypes,
                                     index_value=out_df.index_value,
                                     columns_value=out_df.columns_value)