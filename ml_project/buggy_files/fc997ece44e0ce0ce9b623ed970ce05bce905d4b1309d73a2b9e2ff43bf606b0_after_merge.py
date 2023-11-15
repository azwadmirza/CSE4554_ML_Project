def guess_multiscale(data):
    """Guess whether the passed data is multiscale, process it accordingly.

    If shape of arrays along first axis is strictly decreasing, the data is
    multiscale. If it is the same shape everywhere, it is not. Various
    ambiguous conditions in between will result in a ValueError being raised,
    or in an "unwrapping" of data, if data contains only one element.

    Parameters
    ----------
    data : array or list of array
        Data that should be checked.

    Returns
    -------
    multiscale : bool
        True if the data is thought to be multiscale, False otherwise.
    data : list or array
        The input data, perhaps with the leading axis removed.
    """
    # If the data has ndim and is not one-dimensional then cannot be multiscale
    # If data is a zarr array, this check ensure that subsets of it are not
    # instantiated. (`for d in data` instantiates `d` as a NumPy array if
    # `data` is a zarr array.)
    if hasattr(data, 'ndim') and data.ndim > 1:
        return False, data

    shapes = [d.shape for d in data]
    sizes = np.array([np.prod(shape, dtype=np.uint64) for shape in shapes])
    if len(sizes) == 1 and (isinstance(data, list) or isinstance(data, tuple)):
        # pyramid with only one level, unwrap
        return False, data[0]
    if len(sizes) > 1:
        consistent = bool(np.all(sizes[:-1] > sizes[1:]))
        flat = bool(np.all(sizes == sizes[0]))
        if flat:
            # note: the individual array case should be caught by the first
            # code line in this function, hasattr(ndim) and ndim > 1.
            raise ValueError(
                'Input data should be an array-like object, or a sequence of '
                'arrays of decreasing size. Got arrays of single shape: '
                f'{shapes[0]}'
            )
        if not consistent:
            raise ValueError(
                'Input data should be an array-like object, or a sequence of '
                'arrays of decreasing size. Got arrays in incorrect order, '
                f'shapes: {shapes}'
            )
        return True, data
    else:
        return False, data