def scatter_matrix(frame, alpha=0.5, figsize=None, **kwds):
    """
    Draw a matrix of scatter plots.

    Parameters
    ----------
    kwds : other plotting keyword arguments
        To be passed to scatter function

    Examples
    --------
    >>> df = DataFrame(np.random.randn(1000, 4), columns=['A','B','C','D'])
    >>> scatter_matrix(df, alpha=0.2)
    """
    df = frame._get_numeric_data()
    n = df.columns.size
    fig, axes = _subplots(nrows=n, ncols=n, figsize=figsize)

    # no gaps between subplots
    fig.subplots_adjust(wspace=0, hspace=0)

    for i, a in zip(range(n), df.columns):
        for j, b in zip(range(n), df.columns):
            axes[i, j].scatter(df[b], df[a], alpha=alpha, **kwds)
            axes[i, j].yaxis.set_visible(False)
            axes[i, j].xaxis.set_visible(False)

            # setup labels
            if i == 0 and j % 2 == 1:
                axes[i, j].set_xlabel(b, visible=True)
                axes[i, j].xaxis.set_visible(True)
                axes[i, j].xaxis.set_ticks_position('top')
                axes[i, j].xaxis.set_label_position('top')
            if i == n - 1 and j % 2 == 0:
                axes[i, j].set_xlabel(b, visible=True)
                axes[i, j].xaxis.set_visible(True)
                axes[i, j].xaxis.set_ticks_position('bottom')
                axes[i, j].xaxis.set_label_position('bottom')
            if j == 0 and i % 2 == 0:
                axes[i, j].set_ylabel(a, visible=True)
                axes[i, j].yaxis.set_visible(True)
                axes[i, j].yaxis.set_ticks_position('left')
                axes[i, j].yaxis.set_label_position('left')
            if j == n - 1 and i % 2 == 1:
                axes[i, j].set_ylabel(a, visible=True)
                axes[i, j].yaxis.set_visible(True)
                axes[i, j].yaxis.set_ticks_position('right')
                axes[i, j].yaxis.set_label_position('right')

    # ensure {x,y}lim off diagonal are the same as diagonal
    for i in range(n):
        for j in range(n):
            if i != j:
                axes[i, j].set_xlim(axes[j, j].get_xlim())
                axes[i, j].set_ylim(axes[i, i].get_ylim())

    return axes