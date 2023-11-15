    def tile(cls, op):
        a, b = op.inputs
        tensor = op.outputs[0]
        # the axes to align on
        a_axes = lrange(a.ndim - 2)[::-1] + [tensor.ndim - 2, tensor.ndim - 1]
        b_axes = lrange(b.ndim - 2)[::-1] + [tensor.ndim - 1, tensor.ndim]
        a, b = unify_chunks((a, a_axes), (b, b_axes))

        get_nsplit = lambda i: a.nsplits[i] if a.nsplits[i] != (1,) else b.nsplits[i]
        get_idx = lambda ch, idx: tuple(0 if ch.nsplits[j] == (1,) else ix for j, ix in enumerate(idx))

        prefix_idxes = [range(len(get_nsplit(i))) for i in range(a.ndim - 2)]
        out_idxes = prefix_idxes + [range(len(a.nsplits[-2])), range(len(b.nsplits[-1]))]

        out_chunks = []
        for out_idx in itertools.product(*out_idxes):
            chunks = []
            get_s = lambda x, idx: x[idx] if x != (1,) else x[0]
            shape = tuple(max(get_s(a_s, j), get_s(b_s, j))
                          for a_s, b_s, j in zip(a.nsplits[:-2], b.nsplits[:-2], out_idx[:-2])) + \
                    (get_s(a.nsplits[-2], out_idx[-2]), get_s(b.nsplits[-1], out_idx[-1]))

            for contract_idx in range(len(a.nsplits[-1])):
                a_idx = get_idx(a, out_idx[: a.ndim - 1] + (contract_idx,))
                a_chunk = a.cix[a_idx]
                b_idx = get_idx(b, out_idx[: b.ndim - 2] + (contract_idx,) + out_idx[-1:])
                b_chunk = b.cix[b_idx]
                chunk_op = op.copy().reset_key()
                c = chunk_op.new_chunk([a_chunk, b_chunk], shape)
                chunks.append(c)

            if len(chunks) == 1:
                c = chunks[0]
                out_chunk_op = c.op.copy()
                out_chunk = out_chunk_op.new_chunk(out_chunk_op.inputs, c.shape, index=out_idx)
            else:
                out_chunk = tree_add(tensor.op.dtype, chunks, out_idx, shape)

            out_chunks.append(out_chunk)

        nsplits = tuple(get_nsplit(i) for i in range(a.ndim - 2)) + (a.nsplits[-2], b.nsplits[-1])
        new_op = op.copy()
        return new_op.new_tensors([a, b], tensor.shape, chunks=out_chunks, nsplits=nsplits)