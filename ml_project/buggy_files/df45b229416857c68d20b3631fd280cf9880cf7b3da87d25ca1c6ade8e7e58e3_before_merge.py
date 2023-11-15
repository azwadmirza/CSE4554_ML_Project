    def tile(cls, op):
        x = op.input
        axis = op.axis
        ord = op.ord
        keepdims = op.keepdims

        axis_chunk_shapes = tuple(x.chunk_shape[i] for i in axis)
        can_apply_norm = all(s == 1 for s in axis_chunk_shapes)

        if can_apply_norm:
            axis_set = set(axis)
            get_shape = lambda shape: tuple(s if i not in axis_set else 1 for i, s in enumerate(shape)
                                            if i not in axis_set or keepdims)

            out_chunk_shape = get_shape(x.chunk_shape)
            out_chunks = []
            for idx in itertools.product(*[range(s) for s in out_chunk_shape]):
                idx_iter = iter(idx)
                in_idx = tuple(0 if i in axis_set and not keepdims else next(idx_iter)
                               for i in range(x.ndim))

                c = x.cix[in_idx]
                chunk_op = op.copy().reset_key()
                out_chunk = chunk_op.new_chunk([c], shape=get_shape(c.shape), index=idx)
                out_chunks.append(out_chunk)

            nsplits = [tuple(c.shape[i] for c in out_chunks
                             if all(idx == 0 for j, idx in enumerate(c.index) if j != i))
                       for i in range(len(out_chunks[0].shape))]
            new_op = op.copy()
            return new_op.new_tensors(op.inputs, op.outputs[0].shape, chunks=out_chunks, nsplits=nsplits)

        r = cls._norm(x.astype(op.outputs[0].dtype), ord, axis, keepdims)
        recursive_tile(r)
        new_op = op.copy()
        return new_op.new_tensors(op.inputs, op.outputs[0].shape, chunks=r.chunks, nsplits=r.nsplits)