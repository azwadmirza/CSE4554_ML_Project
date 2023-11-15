    def tile(cls, op):
        tensor = op.outputs[0]

        out_chunks = []
        for c in op.inputs[0].chunks:
            chunk_op = op.copy().reset_key()
            chunk_shape = tuple(s if np.isnan(s) else int(s)
                                for s in _reorder(c.shape, op.axes))
            chunk_idx = _reorder(c.index, op.axes)
            out_chunk = chunk_op.new_chunk([c], shape=chunk_shape,
                                           index=chunk_idx, order=tensor.order)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        nsplits = _reorder(op.inputs[0].nsplits, op.axes)
        return new_op.new_tensors(op.inputs, op.outputs[0].shape, order=tensor.order,
                                  chunks=out_chunks, nsplits=nsplits)