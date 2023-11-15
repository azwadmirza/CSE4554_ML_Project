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
    def f(x):
        if isinstance(x, dict):
            return x.get(i)
        elif len(x) > i >= -len(x):
            return x[i]
        return np.nan
    return _na_map(f, arr)