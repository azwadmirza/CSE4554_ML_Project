def agg(groupby, func, method='auto', *args, **kwargs):
    """
    Aggregate using one or more operations on grouped data.

    Parameters
    ----------
    groupby : Mars Groupby
        Groupby data.
    func : str or list-like
        Aggregation functions.
    method : {'auto', 'shuffle', 'tree'}, default 'auto'
        'tree' method provide a better performance, 'shuffle' is recommended
        if aggregated result is very large, 'auto' will use 'shuffle' method
        in distributed mode and use 'tree' in local mode.

    Returns
    -------
    Series or DataFrame
        Aggregated result.
    """

    # When perform a computation on the grouped data, we won't shuffle
    # the data in the stage of groupby and do shuffle after aggregation.
    if not isinstance(groupby, GROUPBY_TYPE):
        raise TypeError(f'Input should be type of groupby, not {type(groupby)}')

    if method not in ['shuffle', 'tree', 'auto']:
        raise ValueError(f"Method {method} is not available, "
                         "please specify 'tree' or 'shuffle")

    if not _check_if_func_available(func):
        return groupby.transform(func, *args, _call_agg=True, **kwargs)

    agg_op = DataFrameGroupByAgg(func=func, method=method, raw_func=func,
                                 groupby_params=groupby.op.groupby_params)
    return agg_op(groupby)