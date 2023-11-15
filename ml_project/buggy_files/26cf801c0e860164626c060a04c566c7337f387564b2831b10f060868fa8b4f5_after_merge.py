def str_split(arr, pat=None, n=0):
    """
    Split each string (a la re.split) in array by given pattern, propagating NA
    values

    Parameters
    ----------
    pat : string, default None
        String or regular expression to split on. If None, splits on whitespace
    n : int, default 0 (all)

    Returns
    -------
    split : array
    """
    if pat is None:
        f = lambda x: x.split()
    else:
        regex = re.compile(pat)
        f = lambda x: regex.split(x, maxsplit=n)

    return _na_map(f, arr)