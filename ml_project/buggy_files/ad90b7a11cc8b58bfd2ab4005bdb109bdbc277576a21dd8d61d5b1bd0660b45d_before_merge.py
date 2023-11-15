def boxplot(data, column=None, by=None, ax=None, fontsize=None,
            rot=0, grid=True, figsize=None, **kwds):
    """
    Make a box plot from DataFrame column optionally grouped b ysome columns or
    other inputs

    Parameters
    ----------
    data : DataFrame or Series
    column : column name or list of names, or vector
        Can be any valid input to groupby
    by : string or sequence
        Column in the DataFrame to group by
    fontsize : int or string
    rot : label rotation angle
    kwds : other plotting keyword arguments to be passed to matplotlib boxplot
           function

    Returns
    -------
    ax : matplotlib.axes.AxesSubplot
    """
    from pandas import Series, DataFrame
    if isinstance(data, Series):
        data = DataFrame({'x' : data})
        column = 'x'

    def plot_group(grouped, ax):
        keys, values = zip(*grouped)
        keys = [_stringify(x) for x in keys]
        values = [remove_na(v) for v in values]
        ax.boxplot(values, **kwds)
        if kwds.get('vert', 1):
            ax.set_xticklabels(keys, rotation=rot, fontsize=fontsize)
        else:
            ax.set_yticklabels(keys, rotation=rot, fontsize=fontsize)

    if column == None:
        columns = None
    else:
        if isinstance(column, (list, tuple)):
            columns = column
        else:
            columns = [column]

    if by is not None:
        if not isinstance(by, (list, tuple)):
            by = [by]

        fig, axes = _grouped_plot_by_column(plot_group, data, columns=columns,
                                            by=by, grid=grid, figsize=figsize)

        # Return axes in multiplot case, maybe revisit later # 985
        ret = axes
    else:
        if ax is None:
            ax = _gca()
        fig = ax.get_figure()
        data = data._get_numeric_data()
        if columns:
            cols = columns
        else:
            cols = data.columns
        keys = [_stringify(x) for x in cols]

        # Return boxplot dict in single plot case

        clean_values = [remove_na(x) for x in data[cols].values.T]
        bp = ax.boxplot(clean_values, **kwds)
        if kwds.get('vert', 1):
            ax.set_xticklabels(keys, rotation=rot, fontsize=fontsize)
        else:
            ax.set_yticklabels(keys, rotation=rot, fontsize=fontsize)
        ax.grid(grid)

        ret = bp

    fig.subplots_adjust(bottom=0.15, top=0.9, left=0.1, right=0.9, wspace=0.2)
    return ret