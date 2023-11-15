def pivot_table(data, values=None, rows=None, cols=None, aggfunc='mean',
                fill_value=None, margins=False):
    """
    Create a spreadsheet-style pivot table as a DataFrame. The levels in the
    pivot table will be stored in MultiIndex objects (hierarchical indexes) on
    the index and columns of the result DataFrame

    Parameters
    ----------
    data : DataFrame
    values : column to aggregate, optional
    rows : list of column names or arrays to group on
        Keys to group on the x-axis of the pivot table
    cols : list of column names or arrays to group on
        Keys to group on the y-axis of the pivot table
    aggfunc : function, default numpy.mean, or list of functions
        If list of functions passed, the resulting pivot table will have
        hierarchical columns whose top level are the function names (inferred
        from the function objects themselves)
    fill_value : scalar, default None
        Value to replace missing values with
    margins : boolean, default False
        Add all row / columns (e.g. for subtotal / grand totals)

    Examples
    --------
    >>> df
       A   B   C      D
    0  foo one small  1
    1  foo one large  2
    2  foo one large  2
    3  foo two small  3
    4  foo two small  3
    5  bar one large  4
    6  bar one small  5
    7  bar two small  6
    8  bar two large  7

    >>> table = pivot_table(df, values='D', rows=['A', 'B'],
    ...                     cols=['C'], aggfunc=np.sum)
    >>> table
              small  large
    foo  one  1      4
         two  6      NaN
    bar  one  5      4
         two  6      7

    Returns
    -------
    table : DataFrame
    """
    rows = _convert_by(rows)
    cols = _convert_by(cols)

    if isinstance(aggfunc, list):
        pieces = []
        keys = []
        for func in aggfunc:
            table = pivot_table(data, values=values, rows=rows, cols=cols,
                                fill_value=fill_value, aggfunc=func,
                                margins=margins)
            pieces.append(table)
            keys.append(func.__name__)
        return concat(pieces, keys=keys, axis=1)

    keys = rows + cols

    values_passed = values is not None
    if values_passed:
        if isinstance(values, (list, tuple)):
            values_multi = True
        else:
            values_multi = False
            values = [values]
    else:
        values = list(data.columns.drop(keys))

    if values_passed:
        to_filter = []
        for x in keys + values:
            try:
                if x in data:
                    to_filter.append(x)
            except TypeError:
                pass
        if len(to_filter) < len(data.columns):
            data = data[to_filter]

    grouped = data.groupby(keys)
    agged = grouped.agg(aggfunc)

    table = agged
    for i in range(len(cols)):
        name = table.index.names[len(rows)]
        table = table.unstack(name)

    if fill_value is not None:
        table = table.fillna(value=fill_value)

    if margins:
        table = _add_margins(table, data, values, rows=rows,
                             cols=cols, aggfunc=aggfunc)

    # discard the top level
    if values_passed and not values_multi:
        table = table[values[0]]

    return table