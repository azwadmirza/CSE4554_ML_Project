    def tile(cls, op):
        ctx = get_context()
        range_ = op.range
        if isinstance(op.bins, str):
            check_chunks_unknown_shape([op.input], TilesError)
        if op.input_min is not None:
            # check if input min and max are calculated
            min_max_chunk_keys = \
                [inp.chunks[0].key for inp in (op.input_min, op.input_max)]
            metas = ctx.get_chunk_metas(min_max_chunk_keys)
            if any(meta is None for meta in metas):
                raise TilesError('`input_min` or `input_max` need be executed first')
            range_results = ctx.get_chunk_results(min_max_chunk_keys)
            # make sure returned bounds are valid
            if all(x.size > 0 for x in range_results):
                range_ = tuple(x[0] for x in range_results)
        if isinstance(op.bins, TENSOR_TYPE):
            # `bins` is a Tensor, needs to be calculated first
            bins_chunk_keys = [c.key for c in op.bins.chunks]
            metas = ctx.get_chunk_metas(bins_chunk_keys)
            if any(meta is None for meta in metas):
                raise TilesError('`bins` should be executed first if it\'s a tensor')
            bin_datas = ctx.get_chunk_results(bins_chunk_keys)
            bins = np.concatenate(bin_datas)
        else:
            bins = op.bins

        bin_edges, _ = _get_bin_edges(op, op.input, bins, range_, op.weights)
        bin_edges = bin_edges._inplace_tile()
        return [bin_edges]