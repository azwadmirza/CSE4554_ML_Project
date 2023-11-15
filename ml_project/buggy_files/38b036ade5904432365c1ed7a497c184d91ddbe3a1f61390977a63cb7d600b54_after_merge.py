    def tile(cls, op):
        from ..indexing.slice import TensorSlice

        in_tensor = op.inputs[0]
        out_tensor = op.outputs[0]
        axis = op.axis
        if not isinstance(axis, int):
            raise ValueError("axis must be a integer")
        axis = validate_axis(in_tensor.ndim, axis)
        if axis is None:
            raise NotImplementedError

        op_type, bin_op_type = getattr(op, '_get_op_types')()

        chunks = []
        for c in in_tensor.chunks:
            chunk_op = op_type(axis=op.axis, dtype=op.dtype)
            chunks.append(chunk_op.new_chunk([c], shape=c.shape,
                                             index=c.index, order=out_tensor.order))
        inter_tensor = copy.copy(in_tensor)
        inter_tensor._chunks = chunks

        slc = tuple(slice(None) if i != axis else slice(-1, None) for i in range(in_tensor.ndim))

        output_chunks = []
        for chunk in chunks:
            if chunk.index[axis] == 0:
                output_chunks.append(chunk)
                continue

            to_cum_chunks = []
            for i in range(chunk.index[axis]):
                to_cum_index = chunk.index[:axis] + (i,) + chunk.index[axis + 1:]
                shape = chunk.shape[:axis] + (1,) + chunk.shape[axis + 1:]
                to_cum_chunk = inter_tensor.cix[to_cum_index]
                slice_op = TensorSlice(slices=slc, dtype=chunk.dtype)
                sliced_chunk = slice_op.new_chunk([to_cum_chunk], shape=shape,
                                                  index=to_cum_index, order=out_tensor.order)
                to_cum_chunks.append(sliced_chunk)
            to_cum_chunks.append(chunk)

            bin_op = bin_op_type(dtype=chunk.dtype)
            output_chunk = bin_op.new_chunk(to_cum_chunks, shape=chunk.shape,
                                            index=chunk.index, order=out_tensor.order)
            output_chunks.append(output_chunk)

        new_op = op.copy()
        return new_op.new_tensors(op.inputs, in_tensor.shape, order=out_tensor.order,
                                  chunks=output_chunks, nsplits=in_tensor.nsplits)