def plot_compare_evokeds(evokeds, picks=None, gfp=False, colors=None,
                         linestyles=['-'], styles=None, cmap=None,
                         vlines="auto", ci=0.95, truncate_yaxis=False,
                         truncate_xaxis=True, ylim=dict(), invert_y=False,
                         show_sensors=None, show_legend=True,
                         split_legend=False, axes=None, title=None, show=True):
    """Plot evoked time courses for one or more conditions and/or channels.

    Parameters
    ----------
    evokeds : instance of mne.Evoked | list | dict
        If a single Evoked instance, it is plotted as a time series.
        If a dict whose values are Evoked objects, the contents are plotted as
        single time series each and the keys are used as condition labels.
        If a list of Evokeds, the contents are plotted with indices as labels.
        If a [dict/list] of lists, the unweighted mean is plotted as a time
        series and the parametric confidence interval is plotted as a shaded
        area. All instances must have the same shape - channel numbers, time
        points etc.
        If dict, keys must be of type str.
    picks : None | int | list of int
        If int or list of int, the indices of the sensors to average and plot.
        If multiple channel types are selected, one figure will be returned for
        each channel type.
        If the selected channels are gradiometers, the signal from
        corresponding (gradiometer) pairs will be combined.
        If None, it defaults to all data channels, in which case the global
        field power will be plotted for all channel type available.
    gfp : bool
        If True, the channel type wise GFP is plotted.
        If `picks` is an empty list (default), this is set to True.
    colors : list | dict | None
        If a list, will be sequentially used for line colors.
        If a dict, can map evoked keys or '/'-separated (HED) tags to
        conditions.
        For example, if `evokeds` is a dict with the keys "Aud/L", "Aud/R",
        "Vis/L", "Vis/R", `colors` can be `dict(Aud='r', Vis='b')` to map both
        Aud/L and Aud/R to the color red and both Visual conditions to blue.
        If None (default), a sequence of desaturated colors is used.
        If `cmap` is None, `colors` will indicate how each condition is
        colored with reference to its position on the colormap - see `cmap`
        below. In that case, the values of colors must be either integers,
        in which case they will be mapped to colors in rank order; or floats
        between 0 and 1, in which case they will be mapped to percentiles of
        the colormap.
    linestyles : list | dict
        If a list, will be sequentially and repeatedly used for evoked plot
        linestyles.
        If a dict, can map the `evoked` keys or '/'-separated (HED) tags to
        conditions.
        For example, if evokeds is a dict with the keys "Aud/L", "Aud/R",
        "Vis/L", "Vis/R", `linestyles` can be `dict(L='--', R='-')` to map both
        Aud/L and Vis/L to dashed lines and both Right-side conditions to
        straight lines.
    styles : dict | None
        If a dict, keys must map to evoked keys or conditions, and values must
        be a dict of legal inputs to `matplotlib.pyplot.plot`. These
        parameters will be passed to the line plot call of the corresponding
        condition, overriding defaults.
        E.g., if evokeds is a dict with the keys "Aud/L", "Aud/R",
        "Vis/L", "Vis/R", `styles` can be `{"Aud/L": {"linewidth": 1}}` to set
        the linewidth for "Aud/L" to 1. Note that HED ('/'-separated) tags are
        not supported.
    cmap : None | str | tuple
        If not None, plot evoked activity with colors from a color gradient
        (indicated by a str referencing a matplotlib colormap - e.g., "viridis"
        or "Reds").
        If ``evokeds`` is a list and ``colors`` is `None`, the color will
        depend on the list position. If ``colors`` is a list, it must contain
        integers where the list positions correspond to ``evokeds``, and the
        value corresponds to the position on the colorbar.
        If ``evokeds`` is a dict, ``colors`` should be a dict mapping from
        (potentially HED-style) condition tags to numbers corresponding to
        positions on the colorbar - rank order for integers, or floats for
        percentiles. E.g., ::

            evokeds={"cond1/A": ev1, "cond2/A": ev2, "cond3/A": ev3, "B": ev4},
            cmap='viridis', colors=dict(cond1=1 cond2=2, cond3=3),
            linestyles={"A": "-", "B": ":"}

        If ``cmap`` is a tuple of length 2, the first item must be
        a string which will become the colorbar label, and the second one
        must indicate a colormap, e.g. ::

            cmap=('conds', 'viridis'), colors=dict(cond1=1 cond2=2, cond3=3),

    vlines : "auto" | list of float
        A list in seconds at which to plot dashed vertical lines.
        If "auto" and the supplied data includes 0, it is set to [0.]
        and a vertical bar is plotted at time 0.
    ci : float | callable | None | bool
        If not None and ``evokeds`` is a [list/dict] of lists, a shaded
        confidence interval is drawn around the individual time series. If
        float, a percentile bootstrap method is used to estimate the confidence
        interval and this value determines the CI width. E.g., if this value is
        .95 (the default), the 95% confidence interval is drawn. If a callable,
        it must take as its single argument an array (observations x times) and
        return the upper and lower confidence bands.
        If None or False, no confidence band is plotted.
        If True, the 95% confidence interval is drawn.
    truncate_yaxis : bool | str
        If True, the left y axis spine is truncated to reduce visual clutter.
        If 'max_ticks', the spine is truncated at the minimum and maximum
        ticks. Else, it is truncated to half the max absolute value, rounded to
        .25. Defaults to False.
    truncate_xaxis : bool
        If True, the x axis is truncated to span from the first to the last.
        xtick. Defaults to True.
    ylim : dict | None
        ylim for plots (after scaling has been applied). e.g.
        ylim = dict(eeg=[-20, 20])
        Valid keys are eeg, mag, grad, misc. If None, the ylim parameter
        for each channel equals the pyplot default.
    invert_y : bool
        If True, negative values are plotted up (as is sometimes done
        for ERPs out of tradition). Defaults to False.
    show_sensors: bool | int | str | None
        If not False, channel locations are plotted on a small head circle.
        If int or str, the position of the axes (forwarded to
        ``mpl_toolkits.axes_grid1.inset_locator.inset_axes``).
        If None, defaults to True if ``gfp`` is False, else to False.
    show_legend : bool | str | int
        If not False, show a legend. If int or str, it is the position of the
        legend axes (forwarded to
        ``mpl_toolkits.axes_grid1.inset_locator.inset_axes``).
    split_legend : bool
        If True, the legend shows color and linestyle separately; `colors` must
        not be None. Defaults to True if ``cmap`` is not None, else defaults to
        False.
    axes : None | `matplotlib.axes.Axes` instance | list of `axes`
        What axes to plot to. If None, a new axes is created.
        When plotting multiple channel types, can also be a list of axes, one
        per channel type.
    title : None | str
        If str, will be plotted as figure title. If None, the channel names
        will be shown.
    show : bool
        If True, show the figure.

    Returns
    -------
    fig : Figure | list of Figures
        The figure(s) in which the plot is drawn. When plotting multiple
        channel types, a list of figures, one for each channel type is
        returned.

    Notes
    -----
    When multiple channels are passed, this function combines them all, to
    get one time course for each condition. If gfp is True it combines
    channels using global field power (GFP) computation, else it is taking
    a plain mean.

    This function is useful for comparing multiple ER[P/F]s - e.g., for
    multiple conditions - at a specific location.

    It can plot:

    - a simple :class:`mne.Evoked` object,
    - a list or dict of :class:`mne.Evoked` objects (e.g., for multiple
      conditions),
    - a list or dict of lists of :class:`mne.Evoked` (e.g., for multiple
      subjects in multiple conditions).

    In the last case, it can show a confidence interval (across e.g. subjects)
    using parametric or bootstrap estimation.

    When ``picks`` includes more than one planar gradiometer, the planar
    gradiometers are combined with RMSE. For example data from a
    VectorView system with 204 gradiometers will be transformed to
    102 channels.
    """
    import matplotlib.pyplot as plt
    import matplotlib.lines as mlines

    evokeds, colors = _format_evokeds_colors(evokeds, cmap, colors)
    conditions = sorted(list(evokeds.keys()))

    # check ci parameter
    if ci is None:
        ci = False
    if ci is True:
        ci = .95
    elif ci is not False and not (isinstance(ci, np.float) or callable(ci)):
        raise TypeError('ci must be None, bool, float or callable, got %s' %
                        type(ci))

    # get and set a few limits and variables (times, channels, units)
    one_evoked = evokeds[conditions[0]][0]
    times = one_evoked.times
    info = one_evoked.info
    tmin, tmax = times[0], times[-1]

    if vlines == "auto" and (tmin < 0 and tmax > 0):
        vlines = [0.]
    if not isinstance(vlines, (list, tuple)):
        raise TypeError(
            "vlines must be a list or tuple, not %s" % type(vlines))

    if isinstance(picks, Integral):
        picks = [picks]
    elif picks is None:
        logger.info("No picks, plotting the GFP ...")
        gfp = True
        picks = _pick_data_channels(info)

    if not isinstance(picks, (list, np.ndarray)):
        raise TypeError("picks should be a list or np.array of integers. "
                        "Got %s." % type(picks))

    if len(picks) == 0:
        raise ValueError("No valid channels were found to plot the GFP. " +
                         "Use 'picks' instead to select them manually.")

    if ylim is None:
        ylim = dict()

    # deal with picks: infer indices and names
    if gfp is True:
        if show_sensors is None:
            show_sensors = False  # don't show sensors for GFP
        ch_names = ['Global Field Power']
        if len(picks) < 2:
            raise ValueError("A GFP with less than 2 channels doesn't work, "
                             "please pick more than %d channels." % len(picks))
    else:
        if show_sensors is None:
            show_sensors = True  # show sensors when not doing GFP
        ch_names = [one_evoked.ch_names[pick] for pick in picks]

    picks_by_types = channel_indices_by_type(info, picks)
    # keep only channel types for which there is a channel:
    ch_types = [t for t in picks_by_types if len(picks_by_types[t]) > 0]

    # let's take care of axis and figs
    if axes is not None:
        if not isinstance(axes, list):
            axes = [axes]
        _validate_if_list_of_axes(axes, obligatory_len=len(ch_types))
    else:
        axes = [plt.subplots(figsize=(8, 6))[1] for _ in range(len(ch_types))]

    if len(ch_types) > 1:
        logger.info("Multiple channel types selected, returning one figure "
                    "per type.")
        figs = list()
        for ii, t in enumerate(ch_types):
            picks_ = picks_by_types[t]
            title_ = "GFP, " + t if (title is None and gfp is True) else title
            figs.append(plot_compare_evokeds(
                evokeds, picks=picks_, gfp=gfp, colors=colors,
                linestyles=linestyles, styles=styles, vlines=vlines, ci=ci,
                truncate_yaxis=truncate_yaxis, ylim=ylim, invert_y=invert_y,
                axes=axes[ii], title=title_, show=show))
        return figs

    # From now on there is only 1 channel type
    assert len(ch_types) == 1
    ch_type = ch_types[0]

    all_positive = gfp  # True if not gfp, False if gfp
    pos_picks = picks  # keep locations to pick for plotting
    if ch_type == "grad" and len(picks) > 1:
        logger.info('Combining all planar gradiometers with RMSE.')
        pos_picks, _ = _grad_pair_pick_and_name(one_evoked.info, picks)
        pos_picks = pos_picks[::2]
        all_positive = True
        for cond, this_evokeds in evokeds.items():
            evokeds[cond] = [_combine_grad(e, picks) for e in this_evokeds]
        ch_names = evokeds[cond][0].ch_names
        picks = range(len(ch_names))

    del info

    ymin, ymax = ylim.get(ch_type, [None, None])

    scaling = _handle_default("scalings")[ch_type]
    unit = _handle_default("units")[ch_type]

    if (ymin is None) and all_positive:
        ymin = 0.  # 'grad' and GFP are plotted as all-positive

    # if we have a dict/list of lists, we compute the grand average and the CI
    _ci_fun = None
    if ci is not False:
        if callable(ci):
            _ci_fun = ci
        else:
            from ..stats import _ci
            _ci_fun = partial(_ci, ci=ci, method="bootstrap")

    # calculate the CI
    ci_dict, data_dict = dict(), dict()
    for cond in conditions:
        this_evokeds = evokeds[cond]
        # this will fail if evokeds do not have the same structure
        # (e.g. channel count)
        data = [e.data[picks, :] * scaling for e in this_evokeds]
        data = np.array(data)
        if gfp:
            data = np.sqrt(np.mean(data * data, axis=1))
        else:
            data = np.mean(data, axis=1)  # average across channels
        if _ci_fun is not None:  # compute CI if requested:
            ci_dict[cond] = _ci_fun(data)
        # average across conditions:
        data_dict[cond] = np.mean(data, axis=0)

    del evokeds

    # we now have dicts for data ('evokeds' - grand averaged Evoked's)
    # and the CI ('ci_array') with cond name labels

    # style the individual condition time series
    # Styles (especially color and linestyle) are pulled from a dict 'styles'.
    # This dict has one entry per condition. Its color and linestyle entries
    # are pulled from the 'colors' and 'linestyles' dicts via '/'-tag matching
    # unless they are overwritten by entries from a user-provided 'styles'.

    # first, copy to avoid overwriting
    styles = deepcopy(styles)
    colors = deepcopy(colors)
    linestyles = deepcopy(linestyles)

    # second, check if input is valid
    if isinstance(styles, dict):
        for style_ in styles:
            if style_ not in conditions:
                raise ValueError("Could not map between 'styles' and "
                                 "conditions. Condition " + style_ +
                                 " was not found in the supplied data.")

    # third, color
    # check: is color a list?
    if (colors is not None and not isinstance(colors, string_types) and
            not isinstance(colors, dict) and len(colors) > 1):
        colors = dict((condition, color) for condition, color
                      in zip(conditions, colors))

    if cmap is not None:
        if not isinstance(cmap, string_types) and len(cmap) == 2:
            cmap_label, cmap = cmap
        else:
            cmap_label = ""

    # dealing with a split legend
    if split_legend is None:
        split_legend = cmap is not None  # default to True iff cmap is given
    if split_legend is True:
        if colors is None:
            raise ValueError(
                "If `split_legend` is True, `colors` must not be None.")
        # mpl 1.3 requires us to split it like this. with recent mpl,
        # we could use the label parameter of the Line2D
        legend_lines, legend_labels = list(), list()
        if cmap is None:  # ... one set of lines for the colors
            for color in sorted(colors.keys()):
                line = mlines.Line2D([], [], linestyle="-",
                                     color=colors[color])
                legend_lines.append(line)
                legend_labels.append(color)
        if len(list(linestyles)) > 1:  # ... one set for the linestyle
            for style, s in linestyles.items():
                line = mlines.Line2D([], [], color='k', linestyle=s)
                legend_lines.append(line)
                legend_labels.append(style)

    styles, the_colors, color_conds, color_order, colors_are_float =\
        _setup_styles(data_dict.keys(), styles, cmap, colors, linestyles)

    # We now have a 'styles' dict with one entry per condition, specifying at
    # least color and linestyles.

    ax, = axes
    del axes

    # the actual plot
    any_negative, any_positive = False, False
    for condition in conditions:
        # plot the actual data ('d') as a line
        d = data_dict[condition].T
        ax.plot(times, d, zorder=1000, label=condition, clip_on=False,
                **styles[condition])
        if np.any(d > 0) or all_positive:
            any_positive = True
        if np.any(d < 0):
            any_negative = True

        # plot the confidence interval if available
        if _ci_fun is not None:
            ci_ = ci_dict[condition]
            ax.fill_between(times, ci_[0].flatten(), ci_[1].flatten(),
                            zorder=9, color=styles[condition]['c'], alpha=.3,
                            clip_on=False)

    # truncate the y axis
    orig_ymin, orig_ymax = ax.get_ylim()
    if not any_positive:
        orig_ymax = 0
    if not any_negative:
        orig_ymin = 0

    ax.set_ylim(orig_ymin if ymin is None else ymin,
                orig_ymax if ymax is None else ymax)

    fraction = 2 if ax.get_ylim()[0] >= 0 else 3

    if truncate_yaxis is not False:
        _, ymax_bound = _truncate_yaxis(
            ax, ymin, ymax, orig_ymin, orig_ymax, fraction,
            any_positive, any_negative, truncate_yaxis)
    else:
        if truncate_yaxis is True and ymin is not None and ymin > 0:
            warn("ymin is all-positive, not truncating yaxis")
        ymax_bound = ax.get_ylim()[-1]

    title = _set_title_multiple_electrodes(
        title, "average" if gfp is False else "gfp", ch_names)
    ax.set_title(title)

    current_ymin = ax.get_ylim()[0]

    # plot v lines
    if invert_y is True and current_ymin < 0:
        upper_v, lower_v = -ymax_bound, ax.get_ylim()[-1]
    else:
        upper_v, lower_v = ax.get_ylim()[0], ymax_bound
    ax.vlines(vlines, upper_v, lower_v, linestyles='--', colors='k',
              linewidth=1., zorder=1)

    _setup_ax_spines(ax, vlines, tmin, tmax, invert_y, ymax_bound, unit,
                     truncate_xaxis)

    # and now for 3 "legends" ..
    # a head plot showing the sensors that are being plotted
    if show_sensors:
        if show_sensors is True:
            ymin, ymax = np.abs(ax.get_ylim())
            show_sensors = "lower right" if ymin > ymax else "upper right"
        try:
            pos = _auto_topomap_coords(one_evoked.info, pos_picks,
                                       ignore_overlap=True, to_sphere=True)
        except ValueError:
            warn("Cannot find channel coordinates in the supplied Evokeds. "
                 "Not showing channel locations.")
        else:
            head_pos = {'center': (0, 0), 'scale': (0.5, 0.5)}
            pos, outlines = _check_outlines(pos, np.array([1, 1]), head_pos)

            if not isinstance(show_sensors, (np.int, bool, str)):
                raise TypeError("show_sensors must be numeric, str or bool, "
                                "not " + str(type(show_sensors)))
            show_sensors = _check_loc_legal(show_sensors, "show_sensors")
            _plot_legend(pos, ["k" for _ in picks], ax, list(), outlines,
                         show_sensors, size=25)

    # the condition legend
    if len(conditions) > 1 and show_legend is not False:
        show_legend = _check_loc_legal(show_legend, "show_legend")
        legend_params = dict(loc=show_legend, frameon=True)
        if split_legend:
            if len(legend_lines) > 1:
                ax.legend(legend_lines, legend_labels,  # see above: mpl 1.3
                          ncol=1 + (len(legend_lines) // 4), **legend_params)
        else:
            ax.legend(ncol=1 + (len(conditions) // 5), **legend_params)

    # the colormap, if `cmap` is provided
    if split_legend and cmap is not None:
        # plot the colorbar ... complicated cause we don't have a heatmap
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        divider = make_axes_locatable(ax)
        ax_cb = divider.append_axes("right", size="5%", pad=0.05)
        if colors_are_float:
            ax_cb.imshow(the_colors[:, np.newaxis, :], interpolation='none',
                         aspect=.05)
            color_ticks = np.array(list(set(colors.values()))) * 100
            ax_cb.set_yticks(color_ticks)
            ax_cb.set_yticklabels(color_ticks)
        else:
            ax_cb.imshow(the_colors[:, np.newaxis, :], interpolation='none')
            ax_cb.set_yticks(np.arange(len(the_colors)))
            ax_cb.set_yticklabels(np.array(color_conds)[color_order])
        ax_cb.yaxis.tick_right()
        ax_cb.set(xticks=(), ylabel=cmap_label)

    plt_show(show)
    return ax.figure