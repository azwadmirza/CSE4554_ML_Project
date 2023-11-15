def scatter_matrix(frame, alpha=0.5, figsize=None, ax=None, grid=False,
                   diagonal='hist', marker='.', **kwds):
    """
    Draw a matrix of scatter plots.

    Parameters
    ----------
    alpha : amount of transparency applied
    figsize : a tuple (width, height) in inches
    ax : Matplotlib axis object
    grid : setting this to True will show the grid
    diagonal : pick between 'kde' and 'hist' for
        either Kernel Density Estimation or Histogram
        plon in the diagonal
    kwds : other plotting keyword arguments
        To be passed to scatter function

    Examples
    --------
    >>> df = DataFrame(np.random.randn(1000, 4), columns=['A','B','C','D'])
    >>> scatter_matrix(df, alpha=0.2)
    """
    from matplotlib.artist import setp

    df = frame._get_numeric_data()
    n = df.columns.size
    fig, axes = _subplots(nrows=n, ncols=n, figsize=figsize, ax=ax,
                          squeeze=False)

    # no gaps between subplots
    fig.subplots_adjust(wspace=0, hspace=0)

    mask = com.notnull(df)

    marker = _get_marker_compat(marker)

    for i, a in zip(range(n), df.columns):
        for j, b in zip(range(n), df.columns):
            ax = axes[i, j]

            if i == j:
                values = df[a].values[mask[a].values]

                # Deal with the diagonal by drawing a histogram there.
                if diagonal == 'hist':
                    ax.hist(values)
                elif diagonal in ('kde', 'density'):
                    from scipy.stats import gaussian_kde
                    y = values
                    gkde = gaussian_kde(y)
                    ind = np.linspace(y.min(), y.max(), 1000)
                    ax.plot(ind, gkde.evaluate(ind), **kwds)
            else:
                common = (mask[a] & mask[b]).values

                ax.scatter(df[b][common], df[a][common],
                                   marker=marker, alpha=alpha, **kwds)

            ax.set_xlabel('')
            ax.set_ylabel('')

            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)

            # setup labels
            if i == 0 and j % 2 == 1:
                ax.set_xlabel(b, visible=True)
                ax.xaxis.set_visible(True)
                ax.set_xlabel(b)
                ax.xaxis.set_ticks_position('top')
                ax.xaxis.set_label_position('top')
                setp(ax.get_xticklabels(), rotation=90)
            elif i == n - 1 and j % 2 == 0:
                ax.set_xlabel(b, visible=True)
                ax.xaxis.set_visible(True)
                ax.set_xlabel(b)
                ax.xaxis.set_ticks_position('bottom')
                ax.xaxis.set_label_position('bottom')
                setp(ax.get_xticklabels(), rotation=90)
            elif j == 0 and i % 2 == 0:
                ax.set_ylabel(a, visible=True)
                ax.yaxis.set_visible(True)
                ax.set_ylabel(a)
                ax.yaxis.set_ticks_position('left')
                ax.yaxis.set_label_position('left')
            elif j == n - 1 and i % 2 == 1:
                ax.set_ylabel(a, visible=True)
                ax.yaxis.set_visible(True)
                ax.set_ylabel(a)
                ax.yaxis.set_ticks_position('right')
                ax.yaxis.set_label_position('right')

            # ax.grid(b=grid)

    axes[0, 0].yaxis.set_visible(False)
    axes[n-1, n-1].xaxis.set_visible(False)
    axes[n-1, n-1].yaxis.set_visible(False)
    axes[0, n - 1].yaxis.tick_right()

    for ax in axes.flat:
        setp(ax.get_xticklabels(), fontsize=8)
        setp(ax.get_yticklabels(), fontsize=8)

    return axes