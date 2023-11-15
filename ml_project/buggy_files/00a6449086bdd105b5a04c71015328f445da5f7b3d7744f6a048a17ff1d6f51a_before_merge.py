def rechunk(tensor, chunk_size, threshold=None, chunk_size_limit=None,
            reassign_worker=False):
    chunk_size = get_nsplits(tensor, chunk_size, tensor.dtype.itemsize)
    if chunk_size == tensor.nsplits:
        return tensor

    op = TensorRechunk(chunk_size, threshold, chunk_size_limit, reassign_worker=reassign_worker,
                       dtype=tensor.dtype, sparse=tensor.issparse())
    return op(tensor)