def rechunk(a, chunk_size, threshold=None, chunk_size_limit=None, reassign_worker=False):
    if not any(pd.isna(s) for s in a.shape):
        # do client check only when no unknown shape,
        # real nsplits will be recalculated inside `tile`
        chunk_size = _get_chunk_size(a, chunk_size)
        if chunk_size == a.nsplits:
            return a

    op = DataFrameRechunk(chunk_size=chunk_size, threshold=threshold,
                          chunk_size_limit=chunk_size_limit,
                          reassign_worker=reassign_worker)
    return op(a)