def guess_multiscale(data):
    """Guess if the passed data is multiscale of not.

    If shape of arrays along first axis is strictly decreasing.

    Parameters
    ----------
    data : array or list of array
        Data that should be checked.

    Returns
    -------
    bool
        If data is multiscale or not.
    """
    # If the data has ndim and is not one-dimensional then cannot be multiscale
    if hasattr(data, 'ndim') and data.ndim > 1:
        return False

    size = np.array([np.prod(d.shape, dtype=np.uint64) for d in data])
    if len(size) > 1:
        return bool(np.all(size[:-1] > size[1:]))
    else:
        return False