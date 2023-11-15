def str_get(arr, i):
    """
    Extract element from lists, tuples, or strings in each element in the
    Series/Index.

    Parameters
    ----------
    i : int
        Integer index (location)

    Returns
    -------
    items : Series/Index of objects
    """
    f = lambda x: x[i] if len(x) > i >= -len(x) else np.nan
    return _na_map(f, arr)