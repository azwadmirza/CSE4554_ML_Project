def str_replace(arr, pat, repl, n=-1, case=True, flags=0):
    """
    Replace occurrences of pattern/regex in the Series/Index with
    some other string. Equivalent to :meth:`str.replace` or
    :func:`re.sub`.

    Parameters
    ----------
    pat : string
        Character sequence or regular expression
    repl : string
        Replacement sequence
    n : int, default -1 (all)
        Number of replacements to make from start
    case : boolean, default True
        If True, case sensitive
    flags : int, default 0 (no flags)
        re module flags, e.g. re.IGNORECASE

    Returns
    -------
    replaced : Series/Index of objects
    """

    # Check whether repl is valid (GH 13438)
    if not is_string_like(repl):
        raise TypeError("repl must be a string")
    use_re = not case or len(pat) > 1 or flags

    if use_re:
        if not case:
            flags |= re.IGNORECASE
        regex = re.compile(pat, flags=flags)
        n = n if n >= 0 else 0

        def f(x):
            return regex.sub(repl, x, count=n)
    else:
        f = lambda x: x.replace(pat, repl, n)

    return _na_map(f, arr)