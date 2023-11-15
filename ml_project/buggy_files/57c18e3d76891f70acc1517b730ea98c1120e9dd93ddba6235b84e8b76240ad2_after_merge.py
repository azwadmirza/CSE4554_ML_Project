def _plot_evoked(evoked, picks, exclude, unit, show,
                 ylim, proj, xlim, hline, units,
                 scalings, titles, axes, plot_type,
                 cmap=None, gfp=False, window_title=None,
                 spatial_colors=False, set_tight_layout=True,
                 selectable=True, zorder='unsorted'):
    """Aux function for plot_evoked and plot_evoked_image (cf. docstrings)

    Extra param is:

    plot_type : str, value ('butterfly' | 'image')
        The type of graph to plot: 'butterfly' plots each channel as a line
        (x axis: time, y axis: amplitude). 'image' plots a 2D image where
        color depicts the amplitude of each channel at a given time point
        (x axis: time, y axis: channel). In 'image' mode, the plot is not
        interactive.
    """
    import matplotlib.pyplot as plt
    from matplotlib import patheffects
    from matplotlib.widgets import SpanSelector
    info = evoked.info
    if axes is not None and proj == 'interactive':
        raise RuntimeError('Currently only single axis figures are supported'
                           ' for interactive SSP selection.')
    if isinstance(gfp, string_types) and gfp != 'only':
        raise ValueError('gfp must be boolean or "only". Got %s' % gfp)
    if cmap == 'interactive':
        cmap = (None, True)
    elif not isinstance(cmap, tuple):
        cmap = (cmap, True)
    scalings = _handle_default('scalings', scalings)
    titles = _handle_default('titles', titles)
    units = _handle_default('units', units)
    # Valid data types ordered for consistency
    valid_channel_types = ['eeg', 'grad', 'mag', 'seeg', 'eog', 'ecg', 'emg',
                           'dipole', 'gof', 'bio', 'ecog']

    if picks is None:
        picks = list(range(info['nchan']))

    bad_ch_idx = [info['ch_names'].index(ch) for ch in info['bads']
                  if ch in info['ch_names']]
    if len(exclude) > 0:
        if isinstance(exclude, string_types) and exclude == 'bads':
            exclude = bad_ch_idx
        elif (isinstance(exclude, list) and
              all(isinstance(ch, string_types) for ch in exclude)):
            exclude = [info['ch_names'].index(ch) for ch in exclude]
        else:
            raise ValueError('exclude has to be a list of channel names or '
                             '"bads"')

        picks = list(set(picks).difference(exclude))
    picks = np.array(picks)

    types = np.array([channel_type(info, idx) for idx in picks])
    n_channel_types = 0
    ch_types_used = []
    for t in valid_channel_types:
        if t in types:
            n_channel_types += 1
            ch_types_used.append(t)

    axes_init = axes  # remember if axes were given as input

    fig = None
    if axes is None:
        fig, axes = plt.subplots(n_channel_types, 1)

    if isinstance(axes, plt.Axes):
        axes = [axes]
    elif isinstance(axes, np.ndarray):
        axes = list(axes)

    if axes_init is not None:
        fig = axes[0].get_figure()
    if window_title is not None:
        fig.canvas.set_window_title(window_title)

    if not len(axes) == n_channel_types:
        raise ValueError('Number of axes (%g) must match number of channel '
                         'types (%d: %s)' % (len(axes), n_channel_types,
                                             sorted(ch_types_used)))

    # instead of projecting during each iteration let's use the mixin here.
    if proj is True and evoked.proj is not True:
        evoked = evoked.copy()
        evoked.apply_proj()

    times = 1e3 * evoked.times  # time in milliseconds
    texts = list()
    idxs = list()
    lines = list()
    selectors = list()  # for keeping reference to span_selectors
    path_effects = [patheffects.withStroke(linewidth=2, foreground="w",
                                           alpha=0.75)]
    gfp_path_effects = [patheffects.withStroke(linewidth=5, foreground="w",
                                               alpha=0.75)]
    for ax, t in zip(axes, ch_types_used):
        line_list = list()  # 'line_list' contains the lines for this axes
        ch_unit = units[t]
        this_scaling = scalings[t]
        if unit is False:
            this_scaling = 1.0
            ch_unit = 'NA'  # no unit
        idx = list(picks[types == t])
        idxs.append(idx)
        if len(idx) > 0:
            # Set amplitude scaling
            D = this_scaling * evoked.data[idx, :]
            # Parameters for butterfly interactive plots
            if plot_type == 'butterfly':
                text = ax.annotate('Loading...', xy=(0.01, 0.1),
                                   xycoords='axes fraction', fontsize=20,
                                   color='green', zorder=3)
                text.set_visible(False)
                if selectable:
                    callback_onselect = partial(
                        _butterfly_onselect, ch_types=ch_types_used,
                        evoked=evoked, text=text)
                    blit = False if plt.get_backend() == 'MacOSX' else True
                    selectors.append(SpanSelector(
                        ax, callback_onselect, 'horizontal', minspan=10,
                        useblit=blit, rectprops=dict(alpha=0.5,
                                                     facecolor='red')))

                gfp_only = (isinstance(gfp, string_types) and gfp == 'only')
                if not gfp_only:
                    if spatial_colors:
                        chs = [info['chs'][i] for i in idx]
                        locs3d = np.array([ch['loc'][:3] for ch in chs])
                        x, y, z = locs3d.T
                        colors = _rgb(info, x, y, z)
                        if t in ('meg', 'mag', 'grad', 'eeg'):
                            layout = find_layout(info, ch_type=t, exclude=[])
                        else:
                            layout = find_layout(info, None, exclude=[])
                        # drop channels that are not in the data

                        used_nm = np.array(_clean_names(info['ch_names']))[idx]
                        names = np.asarray([name for name in used_nm
                                            if name in layout.names])
                        name_idx = [layout.names.index(name) for name in names]
                        if len(name_idx) < len(chs):
                            warn('Could not find layout for all the channels. '
                                 'Legend for spatial colors not drawn.')
                        else:
                            # find indices for bads
                            bads = [np.where(names == bad)[0][0] for bad in
                                    info['bads'] if bad in names]
                            pos, outlines = _check_outlines(layout.pos[:, :2],
                                                            'skirt', None)
                            pos = pos[name_idx]
                            _plot_legend(pos, colors, ax, bads, outlines)
                    else:
                        colors = ['k'] * len(idx)
                        for i in bad_ch_idx:
                            if i in idx:
                                colors[idx.index(i)] = 'r'

                    if zorder == 'std':
                        # find the channels with the least activity
                        # to map them in front of the more active ones
                        z_ord = D.std(axis=1).argsort()
                    elif zorder == 'unsorted':
                        z_ord = list(range(D.shape[0]))
                    elif not callable(zorder):
                        error = ('`zorder` must be a function, "std" '
                                 'or "unsorted", not {0}.')
                        raise TypeError(error.format(type(zorder)))
                    else:
                        z_ord = zorder(D)

                    # plot channels
                    for ch_idx, z in enumerate(z_ord):
                        line_list.append(ax.plot(times, D[ch_idx], picker=3.,
                                                 zorder=1 + z,
                                                 color=colors[ch_idx])[0])

                if gfp:  # 'only' or boolean True
                    gfp_color = 3 * (0.,) if spatial_colors else (0., 1., 0.)
                    this_gfp = np.sqrt((D * D).mean(axis=0))
                    this_ylim = ax.get_ylim() if (ylim is None or t not in
                                                  ylim.keys()) else ylim[t]
                    if not gfp_only:
                        y_offset = this_ylim[0]
                    else:
                        y_offset = 0.
                    this_gfp += y_offset
                    ax.fill_between(times, y_offset, this_gfp, color='none',
                                    facecolor=gfp_color, zorder=1, alpha=0.25)
                    line_list.append(ax.plot(times, this_gfp, color=gfp_color,
                                             zorder=3)[0])
                    ax.text(times[0] + 0.01 * (times[-1] - times[0]),
                            this_gfp[0] + 0.05 * np.diff(ax.get_ylim())[0],
                            'GFP', zorder=4, color=gfp_color,
                            path_effects=gfp_path_effects)
                for ii, line in zip(idx, line_list):
                    if ii in bad_ch_idx:
                        line.set_zorder(2)
                        if spatial_colors:
                            line.set_linestyle("--")
                ax.set_ylabel('data (%s)' % ch_unit)
                # for old matplotlib, we actually need this to have a bounding
                # box (!), so we have to put some valid text here, change
                # alpha and path effects later
                texts.append(ax.text(0, 0, 'blank', zorder=3,
                                     verticalalignment='baseline',
                                     horizontalalignment='left',
                                     fontweight='bold', alpha=0))
            elif plot_type == 'image':
                im = ax.imshow(D, interpolation='nearest', origin='lower',
                               extent=[times[0], times[-1], 0, D.shape[0]],
                               aspect='auto', cmap=cmap[0])
                cbar = plt.colorbar(im, ax=ax)
                cbar.ax.set_title(ch_unit)
                if cmap[1]:
                    ax.CB = DraggableColorbar(cbar, im)
                ax.set_ylabel('channels (%s)' % 'index')
            else:
                raise ValueError("plot_type has to be 'butterfly' or 'image'."
                                 "Got %s." % plot_type)
            if xlim is not None:
                if xlim == 'tight':
                    xlim = (times[0], times[-1])
                ax.set_xlim(xlim)
            if ylim is not None and t in ylim:
                if plot_type == 'butterfly':
                    ax.set_ylim(ylim[t])
                elif plot_type == 'image':
                    im.set_clim(ylim[t])
            ax.set_title(titles[t] + ' (%d channel%s)' % (
                         len(D), 's' if len(D) > 1 else ''))
            ax.set_xlabel('time (ms)')

            if (plot_type == 'butterfly') and (hline is not None):
                for h in hline:
                    c = ('r' if not spatial_colors else 'grey')
                    ax.axhline(h, linestyle='--', linewidth=2, color=c)
        lines.append(line_list)
    if plot_type == 'butterfly':
        params = dict(axes=axes, texts=texts, lines=lines,
                      ch_names=info['ch_names'], idxs=idxs, need_draw=False,
                      path_effects=path_effects, selectors=selectors)
        fig.canvas.mpl_connect('pick_event',
                               partial(_butterfly_onpick, params=params))
        fig.canvas.mpl_connect('button_press_event',
                               partial(_butterfly_on_button_press,
                                       params=params))

    if axes_init is None:
        plt.subplots_adjust(0.175, 0.08, 0.94, 0.94, 0.2, 0.63)

    if proj == 'interactive':
        _check_delayed_ssp(evoked)
        params = dict(evoked=evoked, fig=fig, projs=info['projs'], axes=axes,
                      types=types, units=units, scalings=scalings, unit=unit,
                      ch_types_used=ch_types_used, picks=picks,
                      plot_update_proj_callback=_plot_update_evoked,
                      plot_type=plot_type)
        _draw_proj_checkbox(None, params)

    plt_show(show)
    fig.canvas.draw()  # for axes plots update axes.
    if set_tight_layout:
        tight_layout(fig=fig)

    return fig