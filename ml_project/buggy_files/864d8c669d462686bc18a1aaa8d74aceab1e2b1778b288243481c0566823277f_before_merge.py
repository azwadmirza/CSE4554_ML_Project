def plot_series(series, label=None, kind='line', use_index=True, rot=None,
                xticks=None, yticks=None, xlim=None, ylim=None,
                ax=None, style=None, grid=True, logy=False, **kwds):
    """
    Plot the input series with the index on the x-axis using matplotlib

    Parameters
    ----------
    label : label argument to provide to plot
    kind : {'line', 'bar'}
    rot : int, default 30
        Rotation for tick labels
    use_index : boolean, default True
        Plot index as axis tick labels
    ax : matplotlib axis object
        If not passed, uses gca()
    style : string, default matplotlib default
        matplotlib line style to use

    ax : matplotlib axis object
        If not passed, uses gca()
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
    kwds : keywords
        Options to pass to matplotlib plotting method

    Notes
    -----
    See matplotlib documentation online for more on this subject
    """
    if kind == 'line':
        klass = LinePlot
    elif kind in ('bar', 'barh'):
        klass = BarPlot

    if ax is None:
        ax = _gca()

    # is there harm in this?
    if label is None:
        label = series.name

    plot_obj = klass(series, kind=kind, rot=rot, logy=logy,
                     ax=ax, use_index=use_index, style=style,
                     xticks=xticks, yticks=yticks, xlim=xlim, ylim=ylim,
                     legend=False, grid=grid, label=label, **kwds)

    plot_obj.generate()
    plot_obj.draw()

    return plot_obj.ax