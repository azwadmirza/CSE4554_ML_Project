def str_endswith(arr, pat):
    """
    Return boolean array indicating whether each string ends with passed
    pattern

    Parameters
    ----------
    pat : string
        Character sequence

    Returns
    -------
    endswith : array (boolean)
    """
    f = lambda x: x.endswith(pat)
    return _na_map(f, arr)