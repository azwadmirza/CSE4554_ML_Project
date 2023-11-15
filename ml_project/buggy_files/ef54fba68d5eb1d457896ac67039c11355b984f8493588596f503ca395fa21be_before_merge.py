def _normalize_keyword_aggregation(kwargs):
    """
    Normalize user-provided "named aggregation" kwargs.

    Transforms from the new ``Dict[str, NamedAgg]`` style kwargs
    to the old OrderedDict[str, List[scalar]]].

    Parameters
    ----------
    kwargs : dict

    Returns
    -------
    aggspec : dict
        The transformed kwargs.
    columns : List[str]
        The user-provided keys.
    order : List[Tuple[str, str]]
        Pairs of the input and output column names.

    Examples
    --------
    >>> _normalize_keyword_aggregation({'output': ('input', 'sum')})
    (OrderedDict([('input', ['sum'])]), ('output',), [('input', 'sum')])
    """
    if not PY36:
        kwargs = OrderedDict(sorted(kwargs.items()))

    # Normalize the aggregation functions as Dict[column, List[func]],
    # process normally, then fixup the names.
    # TODO(Py35): When we drop python 3.5, change this to
    # defaultdict(list)
    # TODO: aggspec type: typing.OrderedDict[str, List[AggScalar]]
    # May be hitting https://github.com/python/mypy/issues/5958
    # saying it doesn't have an attribute __name__
    aggspec = OrderedDict()
    order = []
    columns, pairs = list(zip(*kwargs.items()))

    for name, (column, aggfunc) in zip(columns, pairs):
        if column in aggspec:
            aggspec[column].append(aggfunc)
        else:
            aggspec[column] = [aggfunc]
        order.append((column, com.get_callable_name(aggfunc) or aggfunc))
    return aggspec, columns, order