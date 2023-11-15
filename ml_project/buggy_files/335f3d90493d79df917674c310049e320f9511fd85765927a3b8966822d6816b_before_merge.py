def violinplot(vals, groupby=None, inner="box", color=None, positions=None,
               names=None, order=None, bw="scott", widths=.8, alpha=None,
               saturation=.7, join_rm=False, gridsize=100, cut=3,
               inner_kws=None, ax=None, vert=True, **kwargs):

    """Create a violin plot (a combination of boxplot and kernel density plot).

    Parameters
    ----------
    vals : DataFrame, Series, 2D array, or list of vectors.
        Data for plot. DataFrames and 2D arrays are assumed to be "wide" with
        each column mapping to a box. Lists of data are assumed to have one
        element per box.  Can also provide one long Series in conjunction with
        a grouping element as the `groupy` parameter to reshape the data into
        several violins. Otherwise 1D data will produce a single violins.
    groupby : grouping object
        If `vals` is a Series, this is used to group into boxes by calling
        pd.groupby(vals, groupby).
    inner : {'box' | 'stick' | 'points'}
        Plot quartiles or individual sample values inside violin.
    color : mpl color, sequence of colors, or seaborn palette name
        Inner violin colors
    positions : number or sequence of numbers
        Position of first violin or positions of each violin.
    names : list of strings, optional
        Names to plot on x axis; otherwise plots numbers. This will override
        names inferred from Pandas inputs.
    order : list of strings, optional
        If vals is a Pandas object with name information, you can control the
        order of the plot by providing the violin names in your preferred
        order.
    bw : {'scott' | 'silverman' | scalar}
        Name of reference method to determine kernel size, or size as a
        scalar.
    widths : float
        Width of each violin at maximum density.
    alpha : float, optional
        Transparancy of violin fill.
    saturation : float, 0-1
        Saturation relative to the fully-saturated color. Large patches tend
        to look better at lower saturations, so this dims the palette colors
        a bit by default.
    join_rm : boolean, optional
        If True, positions in the input arrays are treated as repeated
        measures and are joined with a line plot.
    gridsize : int
        Number of discrete gridpoints to evaluate the density on.
    cut : scalar
        Draw the estimate to cut * bw from the extreme data points.
    inner_kws : dict, optional
        Keyword arugments for inner plot.
    ax : matplotlib axis, optional
        Axis to plot on, otherwise grab current axis.
    vert : boolean, optional
        If true (default), draw vertical plots; otherwise, draw horizontal
        ones.
    kwargs : additional parameters to fill_betweenx

    Returns
    -------
    ax : matplotlib axis
        Axis with violin plot.

    """

    if ax is None:
        ax = plt.gca()

    # Reshape and find labels for the plot
    vals, xlabel, ylabel, names = _box_reshape(vals, groupby, names, order)

    # Sort out the plot colors
    colors, gray = _box_colors(vals, color, saturation)

    # Initialize the kwarg dict for the inner plot
    if inner_kws is None:
        inner_kws = {}
    inner_kws.setdefault("alpha", .6 if inner == "points" else 1)
    inner_kws["alpha"] *= 1 if alpha is None else alpha
    inner_kws.setdefault("color", gray)
    inner_kws.setdefault("marker", "." if inner == "points" else "")
    lw = inner_kws.pop("lw", 1.5 if inner == "box" else .8)
    inner_kws.setdefault("linewidth", lw)

    # Find where the violins are going
    if positions is None:
        positions = np.arange(1, len(vals) + 1)
    elif not hasattr(positions, "__iter__"):
        positions = np.arange(positions, len(vals) + positions)

    # Set the default linewidth if not provided in kwargs
    try:
        lw = kwargs[({"lw", "linewidth"} & set(kwargs)).pop()]
    except KeyError:
        lw = 1.5

    # Iterate over the variables
    for i, a in enumerate(vals):

        x = positions[i]

        # If we only have a single value, plot a horizontal line
        if len(a) == 1:
            y = a[0]
            if vert:
                ax.plot([x - widths / 2, x + widths / 2], [y, y], **inner_kws)
            else:
                ax.plot([y, y], [x - widths / 2, x + widths / 2], **inner_kws)
            continue

        # Fit the KDE
        try:
            kde = stats.gaussian_kde(a, bw)
        except TypeError:
            kde = stats.gaussian_kde(a)
            if bw != "scott":  # scipy default
                msg = ("Ignoring bandwidth choice, "
                       "please upgrade scipy to use a different bandwidth.")
                warnings.warn(msg, UserWarning)

        # Determine the support region
        if isinstance(bw, str):
            bw_name = "scotts" if bw == "scott" else bw
            _bw = getattr(kde, "%s_factor" % bw_name)() * a.std(ddof=1)
        else:
            _bw = bw
        y = _kde_support(a, _bw, gridsize, cut, (-np.inf, np.inf))
        dens = kde.evaluate(y)
        scl = 1 / (dens.max() / (widths / 2))
        dens *= scl

        # Draw the violin. If vert (default), we will use ``ax.plot`` in the
        # standard way; otherwise, we invert x,y.
        # For this, define a simple wrapper ``ax_plot``
        color = colors[i]
        if vert:
            ax.fill_betweenx(y, x - dens, x + dens, alpha=alpha, color=color)

            def ax_plot(x, y, *args, **kwargs):
                ax.plot(x, y, *args, **kwargs)

        else:
            ax.fill_between(y, x - dens, x + dens, alpha=alpha, color=color)

            def ax_plot(x, y, *args, **kwargs):
                ax.plot(y, x, *args, **kwargs)

        if inner == "box":
            for quant in percentiles(a, [25, 75]):
                q_x = kde.evaluate(quant) * scl
                q_x = [x - q_x, x + q_x]
                ax_plot(q_x, [quant, quant], linestyle=":",  **inner_kws)
            med = np.median(a)
            m_x = kde.evaluate(med) * scl
            m_x = [x - m_x, x + m_x]
            ax_plot(m_x, [med, med], linestyle="--", **inner_kws)
        elif inner == "stick":
            x_vals = kde.evaluate(a) * scl
            x_vals = [x - x_vals, x + x_vals]
            ax_plot(x_vals, [a, a], linestyle="-", **inner_kws)
        elif inner == "points":
            x_vals = [x for _ in a]
            ax_plot(x_vals, a, mew=0, linestyle="", **inner_kws)
        for side in [-1, 1]:
            ax_plot((side * dens) + x, y, c=gray, lw=lw)

    # Draw the repeated measure bridges
    if join_rm:
        ax.plot(range(1, len(vals) + 1), vals,
                color=inner_kws["color"], alpha=2. / 3)

    # Add in semantic labels
    if names is not None:
        if len(vals) != len(names):
            raise ValueError("Length of names list must match nuber of bins")
        names = list(names)

    if vert:
        # Add in semantic labels
        ax.set_xticks(positions)
        ax.set_xlim(positions[0] - .5, positions[-1] + .5)
        ax.set_xticklabels(names)

        if xlabel is not None:
            ax.set_xlabel(xlabel)
        if ylabel is not None:
            ax.set_ylabel(ylabel)
    else:
        # Add in semantic labels
        ax.set_yticks(positions)
        ax.set_yticklabels(names)
        ax.set_ylim(positions[0] - .5, positions[-1] + .5)

        if ylabel is not None:
            ax.set_ylabel(xlabel)
        if xlabel is not None:
            ax.set_xlabel(ylabel)

    ax.xaxis.grid(False)
    return ax