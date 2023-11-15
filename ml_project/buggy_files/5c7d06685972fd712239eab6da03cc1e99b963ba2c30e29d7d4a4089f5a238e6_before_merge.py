def agg(groupby, func, method='tree', *args, **kwargs):
    """
    Aggregate using one or more operations on grouped data.
    :param groupby: Groupby data.
    :param func: Aggregation functions.
    :param method: 'shuffle' or 'tree', 'tree' method provide a better performance, 'shuffle' is recommended
    if aggregated result is very large.
    :return: Aggregated result.
    """

    # When perform a computation on the grouped data, we won't shuffle
    # the data in the stage of groupby and do shuffle after aggregation.
    if not isinstance(groupby, GROUPBY_TYPE):
        raise TypeError('Input should be type of groupby, not %s' % type(groupby))

    if method not in ['shuffle', 'tree']:
        raise ValueError("Method %s is not available, "
                         "please specify 'tree' or 'shuffle" % method)

    if not _check_if_func_available(func):
        return groupby.transform(func, *args, _call_agg=True, **kwargs)

    agg_op = DataFrameGroupByAgg(func=func, method=method, raw_func=func,
                                 groupby_params=groupby.op.groupby_params)
    return agg_op(groupby)