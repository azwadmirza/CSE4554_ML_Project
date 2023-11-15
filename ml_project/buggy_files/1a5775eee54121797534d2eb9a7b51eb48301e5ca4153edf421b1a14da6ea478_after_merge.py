    def tile(cls, op):
        check_chunks_unknown_shape(op.inputs, TilesError)
        out = op.outputs[0]
        new_chunk_size = op.chunk_size
        if isinstance(out, DATAFRAME_TYPE):
            itemsize = max(getattr(dt, 'itemsize', 8) for dt in out.dtypes)
        else:
            itemsize = out.dtype.itemsize
        steps = plan_rechunks(op.inputs[0], new_chunk_size, itemsize,
                              threshold=op.threshold,
                              chunk_size_limit=op.chunk_size_limit)
        for c in steps:
            out = compute_rechunk(out.inputs[0], c)

        return [out]