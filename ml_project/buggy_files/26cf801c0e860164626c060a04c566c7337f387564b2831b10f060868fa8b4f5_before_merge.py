def str_split(arr, pat, n=0):
    """
    Split each string (a la re.split) in array by given pattern, propagating NA
    values

    Parameters
    ----------
    pat : string
        String or regular expression to split on
    n : int, default 0 (all)

    Returns
    -------
    split : array
    """
    regex = re.compile(pat)
    f = lambda x: regex.split(x, maxsplit=n)
    return _na_map(f, arr)