    def tile(cls, op):
        if op.index is None:
            # check all inputs to make sure no unknown chunk shape
            check_chunks_unknown_shape(op.inputs, TilesError)

        if op.input is None:
            return cls._tile_tensor_none(op)

        out_series = op.outputs[0]
        in_tensor = op.inputs[0]
        nsplits = in_tensor.nsplits

        if op.index is not None:
            index_tensor = op.index.rechunk([nsplits[0]])._inplace_tile()
        else:
            index_tensor = None

        index_start = 0
        out_chunks = []
        series_index = out_series.index_value.to_pandas()
        for in_chunk in in_tensor.chunks:
            new_op = op.copy().reset_key()
            new_op.extra_params['index_start'] = index_start
            chunk_inputs = [in_chunk]
            if index_tensor is not None:
                index_chunk = index_tensor.cix[in_chunk.index]
                chunk_inputs.append(index_chunk)
                if isinstance(op.index, INDEX_TYPE):
                    index_value = index_chunk.index_value
                else:
                    index_value = parse_index(pd.Index([], dtype=in_chunk.dtype),
                                              index_chunk, type(new_op).__name__)
            else:
                chunk_pd_index = series_index[index_start: index_start + in_chunk.shape[0]]
                index_value = parse_index(chunk_pd_index, store_data=True)
            index_start += in_chunk.shape[0]
            out_chunk = new_op.new_chunk(chunk_inputs, shape=in_chunk.shape, index=in_chunk.index,
                                         index_value=index_value, name=out_series.name,
                                         dtype=out_series.dtype)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_tileables(op.inputs, shape=out_series.shape, dtype=out_series.dtype,
                                    index_value=out_series.index_value, name=out_series.name,
                                    chunks=out_chunks, nsplits=in_tensor.nsplits)