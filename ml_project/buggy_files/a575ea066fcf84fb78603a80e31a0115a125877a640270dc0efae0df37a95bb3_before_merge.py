    def tile(cls, op):
        from ..indexing.slice import TensorSlice

        inputs = unify_chunks(*op.inputs)
        output = op.outputs[0]
        axis = op.axis

        output_nsplits = inputs[0].nsplits[:axis] + ((1,) * len(inputs),) + \
            inputs[0].nsplits[axis:]
        output_idxes = itertools.product(*[range(len(nsplit)) for nsplit in output_nsplits])

        out_chunks = []
        for idx in output_idxes:
            input_idx = idx[:axis] + idx[axis + 1:]
            i = idx[axis]
            input_chunk = inputs[i].cix[input_idx]
            slices = [slice(None)] * axis + [np.newaxis] + [slice(None)] * (len(input_idx) - axis)
            shape = input_chunk.shape[:axis] + (1,) + input_chunk.shape[axis:]
            chunk_op = TensorSlice(slices=slices, dtype=op.dtype, sparse=op.sparse)
            out_chunk = chunk_op.new_chunk([input_chunk], shape=shape, index=idx, order=output.order)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_tensors(op.inputs, output.shape,
                                  chunks=out_chunks, nsplits=output_nsplits)