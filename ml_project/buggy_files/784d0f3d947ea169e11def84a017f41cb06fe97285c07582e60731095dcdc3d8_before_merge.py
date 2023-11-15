    def _tile_series(cls, op):
        from ..indexing.iloc import SeriesIlocGetItem

        out = op.outputs[0]
        inputs = op.inputs
        out_chunks = []

        if op.axis == 1:
            inputs = [item.rechunk(op.inputs[0].nsplits)._inplace_tile() for item in inputs]

        cum_index = 0
        nsplits = []
        for series in inputs:
            for c in series.chunks:
                if op.axis == 0:
                    index = (c.index[0] + cum_index,)
                    shape = c.shape
                else:
                    index = (c.index[0], cum_index)
                    shape = (c.shape[0], 1)
                iloc_op = SeriesIlocGetItem(indexes=(slice(None),))
                out_chunks.append(iloc_op.new_chunk([c], shape=shape, index=index,
                                                    index_value=c.index_value,
                                                    dtype=c.dtype,
                                                    name=c.name))
            if op.axis == 0:
                nsplits.extend(series.nsplits[0])
                cum_index += len(series.nsplits[op.axis])
            else:
                nsplits.append(1)
                cum_index += 1

        if op.ignore_index:
            out_chunks = standardize_range_index(out_chunks)

        new_op = op.copy()
        if op.axis == 0:
            nsplits = (tuple(nsplits),)
            return new_op.new_seriess(op.inputs, out.shape,
                                      nsplits=nsplits, chunks=out_chunks,
                                      dtype=out.dtype,
                                      index_value=out.index_value,
                                      name=out.name)
        else:
            nsplits = (inputs[0].nsplits[0], tuple(nsplits))
            return new_op.new_dataframes(op.inputs, out.shape,
                                         nsplits=nsplits, chunks=out_chunks,
                                         dtypes=out.dtypes,
                                         index_value=out.index_value,
                                         columns_value=out.columns_value)