    def tile(cls, op):
        tensor = op.outputs[0]
        value = op.value
        is_value_tensor = isinstance(value, TENSOR_TYPE)

        index_tensor_op = TensorIndex(dtype=tensor.dtype, sparse=op.sparse)
        index_tensor = index_tensor_op.new_tensor([op.input], tensor.shape, indexes=op.indexes).single_tiles()

        nsplits = index_tensor.nsplits
        if any(any(np.isnan(ns) for ns in nsplit) for nsplit in nsplits):
            raise NotImplementedError

        if is_value_tensor:
            value = op.value.rechunk(nsplits).single_tiles()

        chunk_mapping = {c.op.input.index: c for c in index_tensor.chunks}
        out_chunks = []
        for chunk in op.input.chunks:
            index_chunk = chunk_mapping.get(chunk.index)
            if index_chunk is None:
                out_chunks.append(chunk)
                continue

            value_chunk = value.cix[index_chunk.index] if is_value_tensor else value
            chunk_op = op.copy().reset_key()
            out_chunk = chunk_op.new_chunk([chunk], chunk.shape, indexes=index_chunk.op.indexes,
                                           value=value_chunk, index=chunk.index)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_tensors([op.input], tensor.shape, indexes=op.indexes, value=op.value,
                                  chunks=out_chunks, nsplits=op.input.nsplits)