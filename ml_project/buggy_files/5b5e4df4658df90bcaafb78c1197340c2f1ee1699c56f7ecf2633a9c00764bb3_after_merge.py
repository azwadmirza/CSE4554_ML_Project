    def tile(cls, op):
        a, b, a_axes, b_axes = op.a, op.b, op.a_axes, op.b_axes

        c = itertools.count(max(a.ndim, b.ndim))
        a_ax = tuple(a_axes.index(i) if i in a_axes else next(c) for i in range(a.ndim))
        b_ax = tuple(b_axes.index(i) if i in b_axes else next(c) for i in range(b.ndim))
        a, b = unify_chunks((a, a_ax), (b, b_ax))

        a_output_indexes = [range(len(a.nsplits[i])) for i in range(a.ndim) if i not in a_axes]
        b_output_indexes = [range(len(b.nsplits[i])) for i in range(b.ndim) if i not in b_axes]
        output_axes = [(0, i) for i in range(a.ndim) if i not in a_axes] + \
                      [(1, i) for i in range(b.ndim) if i not in b_axes]

        out_chunks = []
        for out_idx in itertools.product(*itertools.chain(a_output_indexes, b_output_indexes)):
            a_indexes = [None] * a.ndim
            b_indexes = [None] * b.ndim
            tensor_shape = []
            for i, idx in enumerate(out_idx):
                t_idx, axis = output_axes[i]
                t = (a, b)[t_idx]
                (a_indexes if t_idx == 0 else b_indexes)[axis] = idx
                tensor_shape.append(t.nsplits[axis][idx])
            tensor_shape = tuple(tensor_shape)

            tensordot_chunks = []
            for contract_indexes in itertools.product(*[range(len(a.nsplits[ax])) for ax in a_axes]):
                a_indices, b_indices = list(a_indexes), list(b_indexes)
                for a_axis, contract_index in izip(a_axes, contract_indexes):
                    a_indices[a_axis] = contract_index
                for b_axis, contract_index in izip(b_axes, contract_indexes):
                    b_indices[b_axis] = contract_index

                tensordot_chunk_op = op.copy().reset_key()
                tensordot_chunk = tensordot_chunk_op.new_chunk(
                    [a.cix[tuple(a_indices)], b.cix[tuple(b_indices)]], tensor_shape)
                tensordot_chunks.append(tensordot_chunk)

            if len(tensordot_chunks) == 1:
                c = tensordot_chunks[0]
                chunk_op = c.op.copy()
                chunk = chunk_op.new_chunk(c.inputs, c.shape, index=out_idx)
            else:
                chunk = tree_add(op.dtype, tensordot_chunks, out_idx, tensor_shape, sparse=op.sparse)
            out_chunks.append(chunk)

        get_nsplits = lambda t_idx, i: (a, b)[t_idx].nsplits[i]
        nsplits = [get_nsplits(*it) for it in output_axes]
        new_op = op.copy()
        return new_op.new_tensors([a, b], op.outputs[0].shape,
                                  chunks=out_chunks, nsplits=nsplits)