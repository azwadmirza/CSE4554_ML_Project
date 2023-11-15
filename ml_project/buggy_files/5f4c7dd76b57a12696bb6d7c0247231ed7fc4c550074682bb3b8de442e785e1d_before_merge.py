    def tile(cls, op):
        from ..datasource import arange

        in_tensor = op.input

        flattened = in_tensor.astype(bool).flatten()
        recursive_tile(flattened)
        indices = arange(flattened.size, dtype=np.intp, chunk_size=flattened.nsplits)
        indices = indices[flattened]
        dim_indices = unravel_index(indices, in_tensor.shape)
        [recursive_tile(ind) for ind in dim_indices]

        kws = [{'nsplits': ind.nsplits, 'chunks': ind.chunks, 'shape': o.shape}
               for ind, o in zip(dim_indices, op.outputs)]
        new_op = op.copy()
        return new_op.new_tensors(op.inputs, kws=kws, output_limit=len(kws))