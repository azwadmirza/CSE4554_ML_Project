    def tile(cls, op):
        a = op.input
        repeats = op.repeats
        axis = op.axis
        ax = axis or 0
        out = op.outputs[0]

        check_chunks_unknown_shape(op.inputs, TilesError)

        if isinstance(repeats, TENSOR_TYPE):
            a, repeats = unify_chunks(a, (repeats, (ax,)))

        nsplit = a.nsplits[axis or 0]

        if isinstance(repeats, Integral):
            new_nsplit = []
            for split in nsplit:
                s = max(split // repeats, 1)
                c = split // s
                new_nsplit.extend([s] * c)
                if split % s != 0:
                    new_nsplit.append(split % s)

            a = a.rechunk({ax: new_nsplit})._inplace_tile()

        out_chunks = []
        ax_cum_count = np.cumsum((0,) + a.nsplits[ax])
        is_repeats_ndarray = isinstance(repeats, np.ndarray)
        for out_idx in itertools.product(*[range(len(s)) for s in a.nsplits]):
            in_chunk = a.cix[out_idx]
            ax_idx = out_idx[ax]
            if is_repeats_ndarray:
                start = ax_cum_count[ax_idx]
                stop = ax_cum_count[ax_idx + 1]
                rp = repeats[start: stop]
                size = rp.sum()
            elif not isinstance(repeats, Integral):
                rp = repeats.cix[ax_idx, ]
                size = np.nan
            else:
                rp = repeats
                size = in_chunk.shape[ax] * rp

            chunk_inputs = [in_chunk]
            if isinstance(rp, TENSOR_CHUNK_TYPE):
                chunk_inputs.append(rp)

            chunk_shape = in_chunk.shape[:ax] + (size,) + in_chunk.shape[ax + 1:]
            chunk_op = op.copy().reset_key()
            if len(chunk_inputs) < 2:
                # repeats is not chunk
                chunk_op._repeats = rp
            out_chunk = chunk_op.new_chunk(chunk_inputs, shape=chunk_shape,
                                           index=out_idx, order=out.order)
            out_chunks.append(out_chunk)

        nsplits = [tuple(c.shape[i] for c in out_chunks
                         if all(idx == 0 for j, idx in enumerate(c.index) if j != i))
                   for i in range(len(out_chunks[0].shape))]
        new_op = op.copy()
        return new_op.new_tensors(op.inputs, out.shape, order=out.order,
                                  chunks=out_chunks, nsplits=nsplits)