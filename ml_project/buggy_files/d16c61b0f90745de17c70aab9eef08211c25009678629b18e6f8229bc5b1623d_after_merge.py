def last_item(x):
    """Returns the last item of an array in a list or an empty list."""
    if x.size == 0:
        # work around for https://github.com/numpy/numpy/issues/5195
        return []

    indexer = (slice(-1, None),) * x.ndim
    return np.ravel(x[indexer]).tolist()