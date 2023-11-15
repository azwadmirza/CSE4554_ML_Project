def hist_frame(data, grid=True, xlabelsize=None, xrot=None,
               ylabelsize=None, yrot=None, ax=None, **kwds):
    """
    Draw Histogram the DataFrame's series using matplotlib / pylab.

    Parameters
    ----------
    grid : boolean, default True
        Whether to show axis grid lines
    xlabelsize : int, default None
        If specified changes the x-axis label size
    xrot : float, default None
        rotation of x axis labels
    ylabelsize : int, default None
        If specified changes the y-axis label size
    yrot : float, default None
        rotation of y axis labels
    ax : matplotlib axes object, default None
    kwds : other plotting keyword arguments
        To be passed to hist function
    """
    import matplotlib.pyplot as plt
    n = len(data.columns)
    rows, cols = 1, 1
    while rows * cols < n:
        if cols > rows:
            rows += 1
        else:
            cols += 1
    _, axes = _subplots(nrows=rows, ncols=cols, ax=ax, squeeze=False)

    for i, col in enumerate(com._try_sort(data.columns)):
        ax = axes[i / cols][i % cols]
        ax.xaxis.set_visible(True)
        ax.yaxis.set_visible(True)
        ax.hist(data[col].dropna().values, **kwds)
        ax.set_title(col)
        ax.grid(grid)

        if xlabelsize is not None:
            plt.setp(ax.get_xticklabels(), fontsize=xlabelsize)
        if xrot is not None:
            plt.setp(ax.get_xticklabels(), rotation=xrot)
        if ylabelsize is not None:
            plt.setp(ax.get_yticklabels(), fontsize=ylabelsize)
        if yrot is not None:
            plt.setp(ax.get_yticklabels(), rotation=yrot)

    for j in range(i + 1, rows * cols):
        ax = axes[j / cols, j % cols]
        ax.set_visible(False)

    ax.get_figure().subplots_adjust(wspace=0.3, hspace=0.3)

    return axes