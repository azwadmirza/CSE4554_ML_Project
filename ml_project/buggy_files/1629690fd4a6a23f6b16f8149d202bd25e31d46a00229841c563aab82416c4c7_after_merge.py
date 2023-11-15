    def tile(cls, op):
        tensor = op.outputs[0]

        v = op.input
        k = op.k
        idx = itertools.count(0)
        if v.ndim == 2:
            check_chunks_unknown_shape(op.inputs, TilesError)
            chunks = []
            nsplit = []

            fx = lambda x, y: x - y + k
            in_nsplits = v.nsplits
            cum_size = [np.cumsum(s).tolist() for s in in_nsplits]
            for c in v.chunks:
                i, j = c.index
                ld_pos = cum_size[0][i] - 1, cum_size[1][j] - in_nsplits[1][j]
                ru_pos = cum_size[0][i] - in_nsplits[0][i], cum_size[1][j] - 1

                ld_fx = fx(*ld_pos)
                ru_fx = fx(*ru_pos)

                if (ld_fx > 0 and ru_fx > 0) or (ld_fx < 0 and ru_fx < 0):
                    continue

                lu_pos = ru_pos[0], ld_pos[1]
                chunk_k = fx(*lu_pos)

                chunk_shape = _get_diag_shape(c.shape, chunk_k)
                chunk_idx = (next(idx),)
                chunk_op = op.to_chunk_op(chunk_k)
                chunk = chunk_op.new_chunk([c], shape=chunk_shape,
                                           index=chunk_idx, order=tensor.order)
                nsplit.append(chunk_shape[0])
                chunks.append(chunk)

            new_op = op.copy()
            return new_op.new_tensors(op.inputs, op.outputs[0].shape, order=tensor.order,
                                      chunks=chunks, nsplits=(tuple(nsplit),))
        else:
            return super().tile(op)