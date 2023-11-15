def str_extractall(arr, pat, flags=0):
    r"""
    For each subject string in the Series, extract groups from all
    matches of regular expression pat. When each subject string in the
    Series has exactly one match, extractall(pat).xs(0, level='match')
    is the same as extract(pat).

    .. versionadded:: 0.18.0

    Parameters
    ----------
    pat : str
        Regular expression pattern with capturing groups.
    flags : int, default 0 (no flags)
        A ``re`` module flag, for example ``re.IGNORECASE``. These allow
        to modify regular expression matching for things like case, spaces,
        etc. Multiple flags can be combined with the bitwise OR operator,
        for example ``re.IGNORECASE | re.MULTILINE``.

    Returns
    -------
    DataFrame
        A ``DataFrame`` with one row for each match, and one column for each
        group. Its rows have a ``MultiIndex`` with first levels that come from
        the subject ``Series``. The last level is named 'match' and indexes the
        matches in each item of the ``Series``. Any capture group names in
        regular expression pat will be used for column names; otherwise capture
        group numbers will be used.

    See Also
    --------
    extract : Returns first match only (not all matches).

    Examples
    --------
    A pattern with one group will return a DataFrame with one column.
    Indices with no matches will not appear in the result.

    >>> s = pd.Series(["a1a2", "b1", "c1"], index=["A", "B", "C"])
    >>> s.str.extractall(r"[ab](\d)")
             0
      match
    A 0      1
      1      2
    B 0      1

    Capture group names are used for column names of the result.

    >>> s.str.extractall(r"[ab](?P<digit>\d)")
            digit
      match
    A 0         1
      1         2
    B 0         1

    A pattern with two groups will return a DataFrame with two columns.

    >>> s.str.extractall(r"(?P<letter>[ab])(?P<digit>\d)")
            letter digit
      match
    A 0          a     1
      1          a     2
    B 0          b     1

    Optional groups that do not match are NaN in the result.

    >>> s.str.extractall(r"(?P<letter>[ab])?(?P<digit>\d)")
            letter digit
      match
    A 0          a     1
      1          a     2
    B 0          b     1
    C 0        NaN     1
    """

    regex = re.compile(pat, flags=flags)
    # the regex must contain capture groups.
    if regex.groups == 0:
        raise ValueError("pattern contains no capture groups")

    if isinstance(arr, ABCIndex):
        arr = arr.to_series().reset_index(drop=True)

    names = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    columns = [names.get(1 + i, i) for i in range(regex.groups)]
    match_list = []
    index_list = []
    is_mi = arr.index.nlevels > 1

    for subject_key, subject in arr.iteritems():
        if isinstance(subject, compat.string_types):

            if not is_mi:
                subject_key = (subject_key, )

            for match_i, match_tuple in enumerate(regex.findall(subject)):
                if isinstance(match_tuple, compat.string_types):
                    match_tuple = (match_tuple,)
                na_tuple = [np.NaN if group == "" else group
                            for group in match_tuple]
                match_list.append(na_tuple)
                result_key = tuple(subject_key + (match_i, ))
                index_list.append(result_key)

    from pandas import MultiIndex
    index = MultiIndex.from_tuples(
        index_list, names=arr.index.names + ["match"])

    result = arr._constructor_expanddim(match_list, index=index,
                                        columns=columns)
    return result