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
    df = frame._get_numeric_data()
    n = df.columns.size
    fig, axes = _subplots(nrows=n, ncols=n, figsize=figsize, ax=ax,
                          squeeze=False)

    # no gaps between subplots
    fig.subplots_adjust(wspace=0, hspace=0)

    mask = com.notnull(df)

    for i, a in zip(range(n), df.columns):
        for j, b in zip(range(n), df.columns):
            if i == j:
                values = df[a].values[mask[a].values]

                # Deal with the diagonal by drawing a histogram there.
                if diagonal == 'hist':
                    axes[i, j].hist(values)
                elif diagonal == 'kde':
                    from scipy.stats import gaussian_kde
                    y = values
                    gkde = gaussian_kde(y)
                    ind = np.linspace(y.min(), y.max(), 1000)
                    axes[i, j].plot(ind, gkde.evaluate(ind), **kwds)
            else:
                common = (mask[a] & mask[b]).values

                axes[i, j].scatter(df[b][common], df[a][common],
                                   marker=marker, alpha=alpha, **kwds)

            axes[i, j].set_xlabel('')
            axes[i, j].set_ylabel('')
            axes[i, j].set_xticklabels([])
            axes[i, j].set_yticklabels([])
            ticks = df.index

            is_datetype = ticks.inferred_type in ('datetime', 'date',
                                              'datetime64')

            if ticks.is_numeric() or is_datetype:
                """
                Matplotlib supports numeric values or datetime objects as
                xaxis values. Taking LBYL approach here, by the time
                matplotlib raises exception when using non numeric/datetime
                values for xaxis, several actions are already taken by plt.
                """
                ticks = ticks._mpl_repr()

            # setup labels
            if i == 0 and j % 2 == 1:
                axes[i, j].set_xlabel(b, visible=True)
                #axes[i, j].xaxis.set_visible(True)
                axes[i, j].set_xlabel(b)
                axes[i, j].set_xticklabels(ticks)
                axes[i, j].xaxis.set_ticks_position('top')
                axes[i, j].xaxis.set_label_position('top')
            if i == n - 1 and j % 2 == 0:
                axes[i, j].set_xlabel(b, visible=True)
                #axes[i, j].xaxis.set_visible(True)
                axes[i, j].set_xlabel(b)
                axes[i, j].set_xticklabels(ticks)
                axes[i, j].xaxis.set_ticks_position('bottom')
                axes[i, j].xaxis.set_label_position('bottom')
            if j == 0 and i % 2 == 0:
                axes[i, j].set_ylabel(a, visible=True)
                #axes[i, j].yaxis.set_visible(True)
                axes[i, j].set_ylabel(a)
                axes[i, j].set_yticklabels(ticks)
                axes[i, j].yaxis.set_ticks_position('left')
                axes[i, j].yaxis.set_label_position('left')
            if j == n - 1 and i % 2 == 1:
                axes[i, j].set_ylabel(a, visible=True)
                #axes[i, j].yaxis.set_visible(True)
                axes[i, j].set_ylabel(a)
                axes[i, j].set_yticklabels(ticks)
                axes[i, j].yaxis.set_ticks_position('right')
                axes[i, j].yaxis.set_label_position('right')

            axes[i, j].grid(b=grid)

    return axes