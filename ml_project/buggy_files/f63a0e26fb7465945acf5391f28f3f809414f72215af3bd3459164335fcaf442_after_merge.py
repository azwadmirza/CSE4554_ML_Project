def rechunk(tensor, chunk_size, threshold=None, chunk_size_limit=None,
            reassign_worker=False):
    if not any(np.isnan(s) for s in tensor.shape) and not tensor.is_coarse():
        try:
            check_chunks_unknown_shape([tensor], ValueError)
        except ValueError:
            # due to reason that tensor has unknown chunk shape,
            # just ignore to hand over to operand
            pass
        else:
            # do client check only when tensor has no unknown shape,
            # otherwise, recalculate chunk_size in `tile`
            chunk_size = get_nsplits(tensor, chunk_size, tensor.dtype.itemsize)
            if chunk_size == tensor.nsplits:
                return tensor

    op = TensorRechunk(chunk_size, threshold, chunk_size_limit, reassign_worker=reassign_worker,
                       dtype=tensor.dtype, sparse=tensor.issparse())
    return op(tensor)