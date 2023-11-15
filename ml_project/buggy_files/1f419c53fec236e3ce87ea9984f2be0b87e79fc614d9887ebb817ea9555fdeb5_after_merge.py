def str_contains(arr, pat, case=True, flags=0, na=np.nan):
    """
    Check whether given pattern is contained in each string in the array

    Parameters
    ----------
    pat : string
        Character sequence or regular expression
    case : boolean, default True
        If True, case sensitive
    flags : int, default 0 (no flags)
        re module flags, e.g. re.IGNORECASE
    na : bool, default NaN

    Returns
    -------

    """
    if not case:
        flags |= re.IGNORECASE

    regex = re.compile(pat, flags=flags)

    f = lambda x: bool(regex.search(x))
    return _na_map(f, arr, na)