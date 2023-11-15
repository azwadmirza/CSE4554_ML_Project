def plot_corr(dcorr, xnames=None, ynames=None, title=None, normcolor=False,
              ax=None, cmap='RdYlBu_r'):
    """Plot correlation of many variables in a tight color grid.

    Parameters
    ----------
    dcorr : ndarray
        Correlation matrix, square 2-D array.
    xnames : list of str, optional
        Labels for the horizontal axis.  If not given (None), then the
        matplotlib defaults (integers) are used.  If it is an empty list, [],
        then no ticks and labels are added.
    ynames : list of str, optional
        Labels for the vertical axis.  Works the same way as `xnames`.
        If not given, the same names as for `xnames` are re-used.
    title : str, optional
        The figure title. If None, the default ('Correlation Matrix') is used.
        If ``title=''``, then no title is added.
    normcolor : bool or tuple of scalars, optional
        If False (default), then the color coding range corresponds to the
        range of `dcorr`.  If True, then the color range is normalized to
        (-1, 1).  If this is a tuple of two numbers, then they define the range
        for the color bar.
    ax : Matplotlib AxesSubplot instance, optional
        If `ax` is None, then a figure is created. If an axis instance is
        given, then only the main plot but not the colorbar is created.
    cmap : str or Matplotlib Colormap instance, optional
        The colormap for the plot.  Can be any valid Matplotlib Colormap
        instance or name.

    Returns
    -------
    fig : Matplotlib figure instance
        If `ax` is None, the created figure.  Otherwise the figure to which
        `ax` is connected.

    Examples
    --------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> import statsmodels.graphics.api as smg

    >>> hie_data = sm.datasets.randhie.load_pandas()
    >>> corr_matrix = np.corrcoef(hie_data.data.T)
    >>> smg.plot_corr(corr_matrix, xnames=hie_data.names)
    >>> plt.show()

    """
    if ax is None:
        create_colorbar = True
    else:
        create_colorbar = False

    fig, ax = utils.create_mpl_ax(ax)
    import matplotlib as mpl
    from matplotlib import cm

    nvars = dcorr.shape[0]

    if ynames is None:
        ynames = xnames
    if title is None:
        title = 'Correlation Matrix'
    if isinstance(normcolor, tuple):
        vmin, vmax = normcolor
    elif normcolor:
        vmin, vmax = -1.0, 1.0
    else:
        vmin, vmax = None, None

    axim = ax.imshow(dcorr, cmap=cmap, interpolation='nearest',
                     extent=(0,nvars,0,nvars), vmin=vmin, vmax=vmax)

    # create list of label positions
    labelPos = np.arange(0, nvars) + 0.5

    if not ynames is None:
        ax.set_yticks(labelPos)
        ax.set_yticks(labelPos[:-1]+0.5, minor=True)
        ax.set_yticklabels(ynames[::-1], fontsize='small',
                           horizontalalignment='right')
    elif ynames == []:
        ax.set_yticks([])

    if not xnames is None:
        ax.set_xticks(labelPos)
        ax.set_xticks(labelPos[:-1]+0.5, minor=True)
        ax.set_xticklabels(xnames, fontsize='small', rotation=45,
                           horizontalalignment='right')
    elif xnames == []:
        ax.set_xticks([])

    if not title == '':
        ax.set_title(title)

    if create_colorbar:
        fig.colorbar(axim, use_gridspec=True)
    fig.tight_layout()

    ax.tick_params(which='minor', length=0)
    ax.tick_params(direction='out', top=False, right=False)
    try:
        ax.grid(True, which='minor', linestyle='-', color='w', lw=1)
    except AttributeError:
        # Seems to fail for axes created with AxesGrid.  MPL bug?
        pass

    return fig