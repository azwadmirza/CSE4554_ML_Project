def jointplot(
    *,
    x=None, y=None,
    data=None,
    kind="scatter", color=None, height=6, ratio=5, space=.2,
    dropna=False, xlim=None, ylim=None, marginal_ticks=False,
    joint_kws=None, marginal_kws=None,
    hue=None, palette=None, hue_order=None, hue_norm=None,
    **kwargs
):
    # Avoid circular imports
    from .relational import scatterplot
    from .regression import regplot, residplot
    from .distributions import histplot, kdeplot, _freedman_diaconis_bins

    # Handle deprecations
    if "size" in kwargs:
        height = kwargs.pop("size")
        msg = ("The `size` parameter has been renamed to `height`; "
               "please update your code.")
        warnings.warn(msg, UserWarning)

    # Set up empty default kwarg dicts
    joint_kws = {} if joint_kws is None else joint_kws.copy()
    joint_kws.update(kwargs)
    marginal_kws = {} if marginal_kws is None else marginal_kws.copy()

    # Handle deprecations of distplot-specific kwargs
    distplot_keys = [
        "rug", "fit", "hist_kws", "norm_hist" "hist_kws", "rug_kws",
    ]
    unused_keys = []
    for key in distplot_keys:
        if key in marginal_kws:
            unused_keys.append(key)
            marginal_kws.pop(key)
    if unused_keys and kind != "kde":
        msg = (
            "The marginal plotting function has changed to `histplot`,"
            " which does not accept the following argument(s): {}."
        ).format(", ".join(unused_keys))
        warnings.warn(msg, UserWarning)

    # Validate the plot kind
    plot_kinds = ["scatter", "hist", "hex", "kde", "reg", "resid"]
    _check_argument("kind", plot_kinds, kind)

    # Raise early if using `hue` with a kind that does not support it
    if hue is not None and kind in ["hex", "reg", "resid"]:
        msg = (
            f"Use of `hue` with `kind='{kind}'` is not currently supported."
        )
        raise ValueError(msg)

    # Make a colormap based off the plot color
    # (Currently used only for kind="hex")
    if color is None:
        color = "C0"
    color_rgb = mpl.colors.colorConverter.to_rgb(color)
    colors = [utils.set_hls_values(color_rgb, l=l)  # noqa
              for l in np.linspace(1, 0, 12)]
    cmap = blend_palette(colors, as_cmap=True)

    # Matplotlib's hexbin plot is not na-robust
    if kind == "hex":
        dropna = True

    # Initialize the JointGrid object
    grid = JointGrid(
        data=data, x=x, y=y, hue=hue,
        palette=palette, hue_order=hue_order, hue_norm=hue_norm,
        dropna=dropna, height=height, ratio=ratio, space=space,
        xlim=xlim, ylim=ylim, marginal_ticks=marginal_ticks,
    )

    if grid.hue is not None:
        marginal_kws.setdefault("legend", False)

    # Plot the data using the grid
    if kind.startswith("scatter"):

        joint_kws.setdefault("color", color)
        grid.plot_joint(scatterplot, **joint_kws)

        if grid.hue is None:
            marg_func = histplot
        else:
            marg_func = kdeplot
            marginal_kws.setdefault("fill", True)

        marginal_kws.setdefault("color", color)
        grid.plot_marginals(marg_func, **marginal_kws)

    elif kind.startswith("hist"):

        # TODO process pair parameters for bins, etc. and pass
        # to both jount and marginal plots

        joint_kws.setdefault("color", color)
        grid.plot_joint(histplot, **joint_kws)

        marginal_kws.setdefault("kde", False)
        marginal_kws.setdefault("color", color)

        marg_x_kws = marginal_kws.copy()
        marg_y_kws = marginal_kws.copy()

        pair_keys = "bins", "binwidth", "binrange"
        for key in pair_keys:
            if isinstance(joint_kws.get(key), tuple):
                x_val, y_val = joint_kws[key]
                marg_x_kws.setdefault(key, x_val)
                marg_y_kws.setdefault(key, y_val)

        histplot(data=data, x=x, hue=hue, **marg_x_kws, ax=grid.ax_marg_x)
        histplot(data=data, y=y, hue=hue, **marg_y_kws, ax=grid.ax_marg_y)

    elif kind.startswith("kde"):

        joint_kws.setdefault("color", color)
        grid.plot_joint(kdeplot, **joint_kws)

        marginal_kws.setdefault("color", color)
        if "fill" in joint_kws:
            marginal_kws.setdefault("fill", joint_kws["fill"])

        grid.plot_marginals(kdeplot, **marginal_kws)

    elif kind.startswith("hex"):

        x_bins = min(_freedman_diaconis_bins(grid.x), 50)
        y_bins = min(_freedman_diaconis_bins(grid.y), 50)
        gridsize = int(np.mean([x_bins, y_bins]))

        joint_kws.setdefault("gridsize", gridsize)
        joint_kws.setdefault("cmap", cmap)
        grid.plot_joint(plt.hexbin, **joint_kws)

        marginal_kws.setdefault("kde", False)
        marginal_kws.setdefault("color", color)
        grid.plot_marginals(histplot, **marginal_kws)

    elif kind.startswith("reg"):

        marginal_kws.setdefault("color", color)
        marginal_kws.setdefault("kde", True)
        grid.plot_marginals(histplot, **marginal_kws)

        joint_kws.setdefault("color", color)
        grid.plot_joint(regplot, **joint_kws)

    elif kind.startswith("resid"):

        joint_kws.setdefault("color", color)
        grid.plot_joint(residplot, **joint_kws)

        x, y = grid.ax_joint.collections[0].get_offsets().T
        marginal_kws.setdefault("color", color)
        histplot(x=x, hue=hue, ax=grid.ax_marg_x, **marginal_kws)
        histplot(y=y, hue=hue, ax=grid.ax_marg_y, **marginal_kws)

    return grid