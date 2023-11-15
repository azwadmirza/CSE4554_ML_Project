def plot_evoked_topomap(evoked, times="auto", ch_type=None, layout=None,
                        vmin=None, vmax=None, cmap=None, sensors=True,
                        colorbar=True, scale=None, scale_time=1e3, unit=None,
                        res=64, size=1, cbar_fmt='%3.1f',
                        time_format='%01d ms', proj=False, show=True,
                        show_names=False, title=None, mask=None,
                        mask_params=None, outlines='head', contours=6,
                        image_interp='bilinear', average=None, head_pos=None,
                        axes=None):
    """Plot topographic maps of specific time points of evoked data

    Parameters
    ----------
    evoked : Evoked
        The Evoked object.
    times : float | array of floats | "auto" | "peaks".
        The time point(s) to plot. If "auto", the number of ``axes`` determines
        the amount of time point(s). If ``axes`` is also None, 10 topographies
        will be shown with a regular time spacing between the first and last
        time instant. If "peaks", finds time points automatically by checking
        for local maxima in global field power.
    ch_type : 'mag' | 'grad' | 'planar1' | 'planar2' | 'eeg' | None
        The channel type to plot. For 'grad', the gradiometers are collected in
        pairs and the RMS for each pair is plotted.
        If None, then channels are chosen in the order given above.
    layout : None | Layout
        Layout instance specifying sensor positions (does not need to
        be specified for Neuromag data). If possible, the correct layout file
        is inferred from the data; if no appropriate layout file was found, the
        layout is automatically generated from the sensor locations.
    vmin : float | callable | None
        The value specifying the lower bound of the color range.
        If None, and vmax is None, -vmax is used. Else np.min(data).
        If callable, the output equals vmin(data). Defaults to None.
    vmax : float | callable | None
        The value specifying the upper bound of the color range.
        If None, the maximum absolute value is used. If callable, the output
        equals vmax(data). Defaults to None.
    cmap : matplotlib colormap | None
        Colormap to use. If None, 'Reds' is used for all positive data,
        otherwise defaults to 'RdBu_r'.
    sensors : bool | str
        Add markers for sensor locations to the plot. Accepts matplotlib plot
        format string (e.g., 'r+' for red plusses). If True, a circle will be
        used (via .add_artist). Defaults to True.
    colorbar : bool
        Plot a colorbar.
    scale : dict | float | None
        Scale the data for plotting. If None, defaults to 1e6 for eeg, 1e13
        for grad and 1e15 for mag.
    scale_time : float | None
        Scale the time labels. Defaults to 1e3 (ms).
    unit : dict | str | None
        The unit of the channel type used for colorbar label. If
        scale is None the unit is automatically determined.
    res : int
        The resolution of the topomap image (n pixels along each side).
    size : float
        Side length per topomap in inches.
    cbar_fmt : str
        String format for colorbar values.
    time_format : str
        String format for topomap values. Defaults to "%01d ms"
    proj : bool | 'interactive'
        If true SSP projections are applied before display. If 'interactive',
        a check box for reversible selection of SSP projection vectors will
        be show.
    show : bool
        Show figure if True.
    show_names : bool | callable
        If True, show channel names on top of the map. If a callable is
        passed, channel names will be formatted using the callable; e.g., to
        delete the prefix 'MEG ' from all channel names, pass the function
        lambda x: x.replace('MEG ', ''). If `mask` is not None, only
        significant sensors will be shown.
    title : str | None
        Title. If None (default), no title is displayed.
    mask : ndarray of bool, shape (n_channels, n_times) | None
        The channels to be marked as significant at a given time point.
        Indices set to `True` will be considered. Defaults to None.
    mask_params : dict | None
        Additional plotting parameters for plotting significant sensors.
        Default (None) equals::

            dict(marker='o', markerfacecolor='w', markeredgecolor='k',
                 linewidth=0, markersize=4)

    outlines : 'head' | 'skirt' | dict | None
        The outlines to be drawn. If 'head', the default head scheme will be
        drawn. If 'skirt' the head scheme will be drawn, but sensors are
        allowed to be plotted outside of the head circle. If dict, each key
        refers to a tuple of x and y positions, the values in 'mask_pos' will
        serve as image mask, and the 'autoshrink' (bool) field will trigger
        automated shrinking of the positions due to points outside the outline.
        Alternatively, a matplotlib patch object can be passed for advanced
        masking options, either directly or as a function that returns patches
        (required for multi-axis plots). If None, nothing will be drawn.
        Defaults to 'head'.
    contours : int | False | None
        The number of contour lines to draw. If 0, no contours will be drawn.
    image_interp : str
        The image interpolation to be used. All matplotlib options are
        accepted.
    average : float | None
        The time window around a given time to be used for averaging (seconds).
        For example, 0.01 would translate into window that starts 5 ms before
        and ends 5 ms after a given time point. Defaults to None, which means
        no averaging.
    head_pos : dict | None
        If None (default), the sensors are positioned such that they span
        the head circle. If dict, can have entries 'center' (tuple) and
        'scale' (tuple) for what the center and scale of the head should be
        relative to the electrode locations.
    axes : instance of Axes | list | None
        The axes to plot to. If list, the list must be a list of Axes of the
        same length as ``times`` (unless ``times`` is None). If instance of
        Axes, ``times`` must be a float or a list of one float.
        Defaults to None.

    Returns
    -------
    fig : instance of matplotlib.figure.Figure
       The figure.
    """
    from ..channels import _get_ch_type
    ch_type = _get_ch_type(evoked, ch_type)
    import matplotlib.pyplot as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable  # noqa

    mask_params = _handle_default('mask_params', mask_params)
    mask_params['markersize'] *= size / 2.
    mask_params['markeredgewidth'] *= size / 2.

    picks, pos, merge_grads, names, ch_type = _prepare_topo_plot(
        evoked, ch_type, layout)

    # project before picks
    if proj is True and evoked.proj is not True:
        data = evoked.copy().apply_proj().data
    else:
        data = evoked.data

    evoked = evoked.copy().pick_channels(
        [evoked.ch_names[pick] for pick in picks])

    if axes is not None:
        if isinstance(axes, plt.Axes):
            axes = [axes]
        times = _process_times(evoked, times, n_peaks=len(axes))
    else:
        times = _process_times(evoked, times, n_peaks=None)
    space = 1 / (2. * evoked.info['sfreq'])
    if (max(times) > max(evoked.times) + space or
            min(times) < min(evoked.times) - space):
        raise ValueError('Times should be between {0:0.3f} and '
                         '{1:0.3f}.'.format(evoked.times[0], evoked.times[-1]))
    n_times = len(times)
    nax = n_times + bool(colorbar)
    width = size * nax
    height = size + max(0, 0.1 * (4 - size)) + bool(title) * 0.5
    if axes is None:
        plt.figure(figsize=(width, height))
        axes = list()
        for ax_idx in range(len(times)):
            if colorbar:  # Make room for the colorbar
                axes.append(plt.subplot(1, n_times + 1, ax_idx + 1))
            else:
                axes.append(plt.subplot(1, n_times, ax_idx + 1))
    elif colorbar:
        warn('Colorbar is drawn to the rightmost column of the figure. Be '
             'sure to provide enough space for it or turn it off with '
             'colorbar=False.')
    if len(axes) != n_times:
        raise RuntimeError('Axes and times must be equal in sizes.')

    if ch_type.startswith('planar'):
        key = 'grad'
    else:
        key = ch_type

    scale = _handle_default('scalings', scale)[key]
    unit = _handle_default('units', unit)[key]

    if not show_names:
        names = None

    w_frame = plt.rcParams['figure.subplot.wspace'] / (2 * nax)
    top_frame = max((0.05 if title is None else 0.25), .2 / size)
    fig = axes[0].get_figure()
    fig.subplots_adjust(left=w_frame, right=1 - w_frame, bottom=0,
                        top=1 - top_frame)
    # find first index that's >= (to rounding error) to each time point
    time_idx = [np.where(_time_mask(evoked.times, tmin=t,
                         tmax=None, sfreq=evoked.info['sfreq']))[0][0]
                for t in times]

    if average is None:
        data = data[np.ix_(picks, time_idx)]
    elif isinstance(average, float):
        if not average > 0:
            raise ValueError('The average parameter must be positive. You '
                             'passed a negative value')
        data_ = np.zeros((len(picks), len(time_idx)))
        ave_time = float(average) / 2.
        iter_times = evoked.times[time_idx]
        for ii, (idx, tmin_, tmax_) in enumerate(zip(time_idx,
                                                     iter_times - ave_time,
                                                     iter_times + ave_time)):
            my_range = (tmin_ < evoked.times) & (evoked.times < tmax_)
            data_[:, ii] = data[picks][:, my_range].mean(-1)
        data = data_
    else:
        raise ValueError('The average parameter must be None or a float.'
                         'Check your input.')

    data *= scale
    if merge_grads:
        from ..channels.layout import _merge_grad_data
        data = _merge_grad_data(data)

    images, contours_ = [], []

    if mask is not None:
        _picks = picks[::2 if ch_type not in ['mag', 'eeg'] else 1]
        mask_ = mask[np.ix_(_picks, time_idx)]

    pos, outlines = _check_outlines(pos, outlines, head_pos)
    if outlines is not None:
        image_mask, pos = _make_image_mask(outlines, pos, res)
    else:
        image_mask = None

    vlims = [_setup_vmin_vmax(data[:, i], vmin, vmax, norm=merge_grads)
             for i in range(len(times))]
    vmin = np.min(vlims)
    vmax = np.max(vlims)
    for idx, time in enumerate(times):
        tp, cn = plot_topomap(data[:, idx], pos, vmin=vmin, vmax=vmax,
                              sensors=sensors, res=res, names=names,
                              show_names=show_names, cmap=cmap,
                              mask=mask_[:, idx] if mask is not None else None,
                              mask_params=mask_params, axes=axes[idx],
                              outlines=outlines, image_mask=image_mask,
                              contours=contours, image_interp=image_interp,
                              show=False)

        images.append(tp)
        if cn is not None:
            contours_.append(cn)
        if time_format is not None:
            axes[idx].set_title(time_format % (time * scale_time))

    if title is not None:
        plt.suptitle(title, verticalalignment='top', size='x-large')

    if colorbar:
        # works both when fig axes pre-defined and when not
        n_fig_axes = max(nax, len(fig.get_axes()))
        cax = plt.subplot(1, n_fig_axes + 1, n_fig_axes + 1)
        # resize the colorbar (by default the color fills the whole axes)
        cpos = cax.get_position()
        if size <= 1:
            cpos.x0 = 1 - (.7 + .1 / size) / n_fig_axes
        cpos.x1 = cpos.x0 + .1 / n_fig_axes
        cpos.y0 = .2
        cpos.y1 = .7
        cax.set_position(cpos)
        if unit is not None:
            cax.set_title(unit)
        cbar = fig.colorbar(images[-1], ax=cax, cax=cax, format=cbar_fmt)
        cbar.set_ticks([cbar.vmin, 0, cbar.vmax])

    if proj == 'interactive':
        _check_delayed_ssp(evoked)
        params = dict(evoked=evoked, fig=fig, projs=evoked.info['projs'],
                      picks=picks, images=images, contours=contours_,
                      time_idx=time_idx, scale=scale, merge_grads=merge_grads,
                      res=res, pos=pos, image_mask=image_mask,
                      plot_update_proj_callback=_plot_update_evoked_topomap)
        _draw_proj_checkbox(None, params)

    plt_show(show)
    return fig