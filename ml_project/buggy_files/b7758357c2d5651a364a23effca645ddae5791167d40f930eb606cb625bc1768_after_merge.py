def str_startswith(arr, pat, na=np.nan):
    """
    Return boolean array indicating whether each string starts with passed
    pattern

    Parameters
    ----------
    pat : string
        Character sequence
    na : bool, default NaN

    Returns
    -------
    startswith : array (boolean)
    """
    f = lambda x: x.startswith(pat)
    return _na_map(f, arr, na)