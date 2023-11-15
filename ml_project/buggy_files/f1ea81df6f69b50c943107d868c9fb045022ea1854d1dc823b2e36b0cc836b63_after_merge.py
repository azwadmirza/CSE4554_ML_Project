def regplot(x, y, data=None, corr_func=stats.pearsonr, func_name=None,
            xlabel="", ylabel="", ci=95, size=None, annotloc=None, color=None,
            reg_kws=None, scatter_kws=None, dist_kws=None, text_kws=None):
    """Scatterplot with regreesion line, marginals, and correlation value.

    Parameters
    ----------
    x : sequence or string
        Independent variable.
    y : sequence or string
        Dependent variable.
    data : dataframe, optional
        If dataframe is given, x, and y are interpreted as string keys
        for selecting to dataframe column names.
    corr_func : callable, optional
        Correlation function; expected to take two arrays and return a
        numeric or (statistic, pval) tuple.
    func_name : string, optional
        Use in lieu of function name for fit statistic annotation.
    xlabel, ylabel : string, optional
        Axis label names if inputs are not Pandas objects or to override.
    ci : int or None
        Confidence interval for the regression estimate.
    size: int
        Figure size (will be a square; only need one int).
    annotloc : two or three tuple
        Specified with (xpos, ypos [, horizontalalignment]).
    color : matplotlib color scheme
        Color of everything but the regression line; can be overridden by
        passing `color` to subfunc kwargs.
    {reg, scatter, dist, text}_kws: dicts
        Further keyword arguments for the constituent plots.

    """
    # Interperet inputs
    if data is not None:
        if not xlabel:
            xlabel = x
        if not ylabel:
            ylabel = y
        x = data[x].values
        y = data[y].values
    else:
        if hasattr(x, "name") and not xlabel:
            if x.name is not None:
                xlabel = x.name
        if hasattr(y, "name") and not ylabel:
            if y.name is not None:
                ylabel = y.name
        x = np.asarray(x)
        y = np.asarray(y)

    # Set up the figure and axes
    size = 6 if size is None else size
    fig = plt.figure(figsize=(size, size))
    ax_scatter = fig.add_axes([0.05, 0.05, 0.75, 0.75])
    ax_x_marg = fig.add_axes([0.05, 0.82, 0.75, 0.13])
    ax_y_marg = fig.add_axes([0.82, 0.05, 0.13, 0.75])

    # Plot the scatter
    if scatter_kws is None:
        scatter_kws = {}
    if color is not None and "color" not in scatter_kws:
        scatter_kws.update(color=color)
    marker = scatter_kws.pop("markerstyle", "o")
    alpha_maker = stats.norm(0, 100)
    alpha = alpha_maker.pdf(len(x)) / alpha_maker.pdf(0)
    alpha = max(alpha, .1)
    alpha = scatter_kws.pop("alpha", alpha)
    ax_scatter.plot(x, y, marker, alpha=alpha, mew=0, **scatter_kws)
    ax_scatter.set_xlabel(xlabel)
    ax_scatter.set_ylabel(ylabel)

    # Marginal plots using our distplot function
    if dist_kws is None:
        dist_kws = {}
    if color is not None and "color" not in dist_kws:
        dist_kws.update(color=color)
    if "legend" not in dist_kws:
        dist_kws["legend"] = False
    dist_kws["xlabel"] = False
    distplot(x, ax=ax_x_marg, **dist_kws)
    distplot(y, ax=ax_y_marg, vertical=True, **dist_kws)
    for ax in [ax_x_marg, ax_y_marg]:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    # Regression line plot
    xlim = ax_scatter.get_xlim()
    a, b = np.polyfit(x, y, 1)
    if reg_kws is None:
        reg_kws = {}
    reg_color = reg_kws.pop("color", "#222222")
    ax_scatter.plot(xlim, np.polyval([a, b], xlim),
                    color=reg_color, **reg_kws)

    # Bootstrapped regression standard error
    if ci is not None:
        xx = np.linspace(xlim[0], xlim[1], 100)

        def _bootstrap_reg(x, y):
            fit = np.polyfit(x, y, 1)
            return np.polyval(fit, xx)

        boots = moss.bootstrap(x, y, func=_bootstrap_reg)
        ci_lims = [50 - ci / 2., 50 + ci / 2.]
        ci_band = moss.percentiles(boots, ci_lims, axis=0)
        ax_scatter.fill_between(xx, *ci_band, color=reg_color, alpha=.15)
        ax_scatter.set_xlim(xlim)

    # Calcluate a fit statistic and p value
    if func_name is None:
        func_name = corr_func.__name__
    out = corr_func(x, y)
    try:
        s, p = out
        msg = "%s: %.3f (p=%.3g%s)" % (func_name, s, p, moss.sig_stars(p))
    except TypeError:
        s = corr_func(x, y)
        msg = "%s: %.3f" % (func_name, s)

    if annotloc is None:
        xmin, xmax = xlim
        x_range = xmax - xmin
        # Assume the fit statistic is correlation-esque for some
        # intuition on where the fit annotation should go
        if s < 0:
            xloc, align = xmax - x_range * .02, "right"
        else:
            xloc, align = xmin + x_range * .02, "left"
        ymin, ymax = ax_scatter.get_ylim()
        y_range = ymax - ymin
        yloc = ymax - y_range * .02
    else:
        if len(annotloc) == 3:
            xloc, yloc, align = annotloc
        else:
            xloc, yloc = annotloc
            align = "left"
    if text_kws is None:
        text_kws = {}
    ax_scatter.text(xloc, yloc, msg, ha=align, va="top", **text_kws)

    # Set the axes on the marginal plots
    ax_x_marg.set_xlim(ax_scatter.get_xlim())
    ax_x_marg.set_yticks([])
    ax_y_marg.set_ylim(ax_scatter.get_ylim())
    ax_y_marg.set_xticks([])