    def tile(cls, op):
        check_chunks_unknown_shape(op.inputs, TilesError)
        tensor = op.outputs[0]

        m = op.input
        k = op.k
        is_triu = type(op) == TensorTriu

        fx = lambda x, y: x - y + k
        nsplits = m.nsplits
        cum_size = [np.cumsum(s) for s in nsplits]

        out_chunks = []
        for out_idx in itertools.product(*[range(len(s)) for s in nsplits]):
            i, j = out_idx[-2:]
            ld_pos = cum_size[-2][i] - 1, cum_size[-1][j] - nsplits[-1][j]
            ru_pos = cum_size[-2][i] - nsplits[-2][i], cum_size[-1][j] - 1

            ld_fx = fx(*ld_pos)
            ru_fx = fx(*ru_pos)

            chunk_shape = tuple(nsplits[i][idx] for i, idx in enumerate(out_idx))
            if (is_triu and ld_fx > 0 and ru_fx > 0) or (not is_triu and ld_fx < 0 and ru_fx < 0):
                # does not cross, fill with zeros
                chunk_op = TensorZeros(dtype=op.dtype, gpu=op.gpu, sparse=op.sparse)
                out_chunk = chunk_op.new_chunk(None, shape=chunk_shape,
                                               index=out_idx, order=tensor.order)
            else:
                lu_pos = ru_pos[0], ld_pos[1]
                chunk_k = fx(*lu_pos)

                input_chunk = m.cix[out_idx]
                chunk_op = op.to_chunk_op(chunk_k)
                out_chunk = chunk_op.new_chunk([input_chunk], shape=chunk_shape,
                                               index=out_idx, order=tensor.order)

            out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_tensors(op.inputs, tensor.shape, chunks=out_chunks, nsplits=m.nsplits)