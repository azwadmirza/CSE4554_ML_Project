    def tile(cls, op):
        check_chunks_unknown_shape(op.inputs, TilesError)
        new_chunk_size = op.chunk_size
        steps = plan_rechunks(op.inputs[0], new_chunk_size, op.inputs[0].dtype.itemsize,
                              threshold=op.threshold,
                              chunk_size_limit=op.chunk_size_limit)
        tensor = op.outputs[0]
        for c in steps:
            tensor = compute_rechunk(tensor.inputs[0], c)

        if op.reassign_worker:
            for c in tensor.chunks:
                c.op._reassign_worker = True

        return [tensor]