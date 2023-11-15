def plot_frame(frame=None, x=None, y=None, subplots=False, sharex=True,
               sharey=False, use_index=True, figsize=None, grid=False,
               legend=True, rot=None, ax=None, style=None, title=None, xlim=None,
               ylim=None, logy=False, xticks=None, yticks=None, kind='line',
               sort_columns=False, fontsize=None, secondary_y=False, **kwds):

    """
    Make line or bar plot of DataFrame's series with the index on the x-axis
    using matplotlib / pylab.

    Parameters
    ----------
    x : label or position, default None
    y : label or position, default None
        Allows plotting of one column versus another
    subplots : boolean, default False
        Make separate subplots for each time series
    sharex : boolean, default True
        In case subplots=True, share x axis
    sharey : boolean, default False
        In case subplots=True, share y axis
    use_index : boolean, default True
        Use index as ticks for x axis
    stacked : boolean, default False
        If True, create stacked bar plot. Only valid for DataFrame input
    sort_columns: boolean, default False
        Sort column names to determine plot ordering
    title : string
        Title to use for the plot
    grid : boolean, default True
        Axis grid lines
    legend : boolean, default True
        Place legend on axis subplots

    ax : matplotlib axis object, default None
    style : list or dict
        matplotlib line style per column
    kind : {'line', 'bar', 'barh'}
        bar : vertical bar plot
        barh : horizontal bar plot
    logy : boolean, default False
        For line plots, use log scaling on y axis
    xticks : sequence
        Values to use for the xticks
    yticks : sequence
        Values to use for the yticks
    xlim : 2-tuple/list
    ylim : 2-tuple/list
    rot : int, default None
        Rotation for ticks
    secondary_y : boolean or sequence, default False
        Whether to plot on the secondary y-axis
        If dict then can select which columns to plot on secondary y-axis
    kwds : keywords
        Options to pass to matplotlib plotting method

    Returns
    -------
    ax_or_axes : matplotlib.AxesSubplot or list of them
    """
    kind = _get_standard_kind(kind.lower().strip())
    if kind == 'line':
        klass = LinePlot
    elif kind in ('bar', 'barh'):
        klass = BarPlot
    elif kind == 'kde':
        klass = KdePlot
    else:
        raise ValueError('Invalid chart type given %s' % kind)

    if x is not None:
        if com.is_integer(x) and not frame.columns.holds_integer():
            x = frame.columns[x]
        frame = frame.set_index(x)

    if y is not None:
        if com.is_integer(y) and not frame.columns.holds_integer():
            y = frame.columns[y]
        return plot_series(frame[y], label=y, kind=kind, use_index=True,
                           rot=rot, xticks=xticks, yticks=yticks,
                           xlim=xlim, ylim=ylim, ax=ax, style=style,
                           grid=grid, logy=logy, secondary_y=secondary_y,
                           **kwds)

    plot_obj = klass(frame, kind=kind, subplots=subplots, rot=rot,
                     legend=legend, ax=ax, style=style, fontsize=fontsize,
                     use_index=use_index, sharex=sharex, sharey=sharey,
                     xticks=xticks, yticks=yticks, xlim=xlim, ylim=ylim,
                     title=title, grid=grid, figsize=figsize, logy=logy,
                     sort_columns=sort_columns, secondary_y=secondary_y,
                     **kwds)
    plot_obj.generate()
    plot_obj.draw()
    if subplots:
        return plot_obj.axes
    else:
        return plot_obj.axes[0]