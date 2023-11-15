def str_replace(arr, pat, repl, n=-1, case=True, flags=0):
    """
    Replace occurrences of pattern/regex in the Series/Index with
    some other string. Equivalent to :meth:`str.replace` or
    :func:`re.sub`.

    Parameters
    ----------
    pat : string
        Character sequence or regular expression
    repl : string or callable
        Replacement string or a callable. The callable is passed the regex
        match object and must return a replacement string to be used.
        See :func:`re.sub`.

    .. versionadded:: 0.20.0

    n : int, default -1 (all)
        Number of replacements to make from start
    case : boolean, default True
        If True, case sensitive
    flags : int, default 0 (no flags)
        re module flags, e.g. re.IGNORECASE

    Returns
    -------
    replaced : Series/Index of objects

    Examples
    --------
    When ``repl`` is a string, every ``pat`` is replaced as with
    :meth:`str.replace`. NaN value(s) in the Series are left as is.

    >>> Series(['foo', 'fuz', np.nan]).str.replace('f', 'b')
    0    boo
    1    buz
    2    NaN
    dtype: object

    When ``repl`` is a callable, it is called on every ``pat`` using
    :func:`re.sub`. The callable should expect one positional argument
    (a regex object) and return a string.

    To get the idea:

    >>> Series(['foo', 'fuz', np.nan]).str.replace('f', repr)
    0    <_sre.SRE_Match object; span=(0, 1), match='f'>oo
    1    <_sre.SRE_Match object; span=(0, 1), match='f'>uz
    2                                                  NaN
    dtype: object

    Reverse every lowercase alphabetic word:

    >>> repl = lambda m: m.group(0)[::-1]
    >>> Series(['foo 123', 'bar baz', np.nan]).str.replace(r'[a-z]+', repl)
    0    oof 123
    1    rab zab
    2        NaN
    dtype: object

    Using regex groups:

    >>> pat = r"(?P<one>\w+) (?P<two>\w+) (?P<three>\w+)"
    >>> repl = lambda m: m.group('two').swapcase()
    >>> Series(['Foo Bar Baz', np.nan]).str.replace(pat, repl)
    0    bAR
    1    NaN
    dtype: object
    """

    # Check whether repl is valid (GH 13438, GH 15055)
    if not (is_string_like(repl) or callable(repl)):
        raise TypeError("repl must be a string or callable")
    use_re = not case or len(pat) > 1 or flags or callable(repl)

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