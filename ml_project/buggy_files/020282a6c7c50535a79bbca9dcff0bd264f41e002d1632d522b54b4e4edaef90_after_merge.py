def agg(groupby, func, method='tree'):
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
    elif isinstance(func, list):
        raise NotImplementedError('Function list is not supported now.')

    if method not in ['shuffle', 'tree']:
        raise NotImplementedError('Method %s has not been implemented' % method)

    if isinstance(func, six.string_types):
        funcs = [func]
    elif isinstance(func, dict):
        funcs = func.values()
    else:
        raise NotImplementedError('Type %s is not support' % type(func))
    for f in funcs:
        if f not in ['sum', 'prod', 'min', 'max']:
            raise NotImplementedError('Aggregation function %s has not been supported' % f)

    in_df = groupby.inputs[0]
    agg_op = DataFrameGroupByAgg(func=func, by=groupby.op.by, method=method,
                                 as_index=groupby.op.as_index, sort=groupby.op.sort)
    return agg_op(in_df)