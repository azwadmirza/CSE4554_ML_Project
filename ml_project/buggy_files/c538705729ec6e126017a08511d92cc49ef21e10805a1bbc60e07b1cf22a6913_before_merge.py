    def tile(cls, op):
        if op.inputs:
            check_chunks_unknown_shape(op.inputs, TilesError)
        tensor = op.outputs[0]

        # op can be TensorDiag or TensorEye
        k = op.k
        nsplits = op._get_nsplits(op)

        fx = lambda x, y: x - y + k
        cum_size = [np.cumsum(s) for s in nsplits]
        out_chunks = []
        for out_idx in itertools.product(*[range(len(s)) for s in nsplits]):
            i, j = out_idx
            ld_pos = cum_size[0][i] - 1, cum_size[1][j] - nsplits[1][j]
            ru_pos = cum_size[0][i] - nsplits[0][i], cum_size[1][j] - 1

            ld_fx = fx(*ld_pos)
            ru_fx = fx(*ru_pos)

            chunk_shape = (nsplits[0][i], nsplits[1][j])
            if (ld_fx > 0 and ru_fx > 0) or (ld_fx < 0 and ru_fx < 0):
                # does not cross, fill with zeros
                chunk_op = TensorZeros(dtype=op.dtype, gpu=op.gpu, sparse=op.sparse)
                chunk = chunk_op.new_chunk(None, shape=chunk_shape, index=out_idx)
            else:
                lu_pos = ru_pos[0], ld_pos[1]
                chunk_k = fx(*lu_pos)
                chunk = op._get_chunk(op, chunk_k, chunk_shape, out_idx)

            out_chunks.append(chunk)

        new_op = op.copy()
        return new_op.new_tensors(op.inputs, tensor.shape, chunks=out_chunks,
                                  nsplits=nsplits)