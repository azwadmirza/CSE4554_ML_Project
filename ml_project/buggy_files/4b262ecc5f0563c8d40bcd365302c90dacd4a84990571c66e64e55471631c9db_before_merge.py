def plot_raw_psd(raw, tmin=0., tmax=np.inf, fmin=0, fmax=np.inf, proj=False,
                 n_fft=None, picks=None, ax=None, color='black',
                 area_mode='std', area_alpha=0.33, n_overlap=0,
                 dB=True, estimate='auto', average=False, show=True, n_jobs=1,
                 line_alpha=None, spatial_colors=None, xscale='linear',
                 reject_by_annotation=True, verbose=None):
    """Plot the power spectral density across channels.

    Different channel types are drawn in sub-plots. When the data has been
    processed with a bandpass, lowpass or highpass filter, dashed lines
    indicate the boundaries of the filter (--). The line noise frequency is
    also indicated with a dashed line (-.).

    Parameters
    ----------
    raw : instance of io.Raw
        The raw instance to use.
    tmin : float
        Start time for calculations.
    tmax : float
        End time for calculations.
    fmin : float
        Start frequency to consider.
    fmax : float
        End frequency to consider.
    proj : bool
        Apply projection.
    n_fft : int | None
        Number of points to use in Welch FFT calculations.
        Default is None, which uses the minimum of 2048 and the
        number of time points.
    picks : array-like of int | None
        List of channels to use. Cannot be None if `ax` is supplied. If both
        `picks` and `ax` are None, separate subplots will be created for
        each standard channel type (`mag`, `grad`, and `eeg`).
    ax : instance of matplotlib Axes | None
        Axes to plot into. If None, axes will be created.
    color : str | tuple
        A matplotlib-compatible color to use. Has no effect when
        spatial_colors=True.
    area_mode : str | None
        Mode for plotting area. If 'std', the mean +/- 1 STD (across channels)
        will be plotted. If 'range', the min and max (across channels) will be
        plotted. Bad channels will be excluded from these calculations.
        If None, no area will be plotted. If average=False, no area is plotted.
    area_alpha : float
        Alpha for the area.
    n_overlap : int
        The number of points of overlap between blocks. The default value
        is 0 (no overlap).
    dB : bool
        Plot Power Spectral Density (PSD), in units (amplitude**2/Hz (dB)) if
        ``dB=True``, and ``estimate='power'`` or ``estimate='auto'``. Plot PSD
        in units (amplitude**2/Hz) if ``dB=False`` and,
        ``estimate='power'``. Plot Amplitude Spectral Density (ASD), in units
        (amplitude/sqrt(Hz)), if ``dB=False`` and ``estimate='amplitude'`` or
        ``estimate='auto'``. Plot ASD, in units (amplitude/sqrt(Hz) (db)), if
        ``dB=True`` and ``estimate='amplitude'``.
    estimate : str, {'auto', 'power', 'amplitude'}
        Can be "power" for power spectral density (PSD), "amplitude" for
        amplitude spectrum density (ASD), or "auto" (default), which uses
        "power" when dB is True and "amplitude" otherwise.
    average : bool
        If False (default), the PSDs of all channels is displayed. No averaging
        is done and parameters area_mode and area_alpha are ignored. When
        False, it is possible to paint an area (hold left mouse button and
        drag) to plot a topomap.
    show : bool
        Show figure if True.
    n_jobs : int
        Number of jobs to run in parallel.
    line_alpha : float | None
        Alpha for the PSD line. Can be None (default) to use 1.0 when
        ``average=True`` and 0.1 when ``average=False``.
    spatial_colors : bool
        Whether to use spatial colors. Only used when ``average=False``.
    xscale : str
        Can be 'linear' (default) or 'log'.
    reject_by_annotation : bool
        Whether to omit bad segments from the data while computing the
        PSD. If True, annotated segments with a description that starts
        with 'bad' are omitted. Has no effect if ``inst`` is an Epochs or
        Evoked object. Defaults to True.

        .. versionadded:: 0.15.0
    verbose : bool, str, int, or None
        If not None, override default verbose level (see :func:`mne.verbose`
        and :ref:`Logging documentation <tut_logging>` for more).

    Returns
    -------
    fig : instance of matplotlib figure
        Figure with frequency spectra of the data channels.
    """
    from matplotlib.ticker import ScalarFormatter

    if average and spatial_colors:
        raise ValueError('Average and spatial_colors cannot be enabled '
                         'simultaneously.')
    if spatial_colors is None:
        spatial_colors = False if average else True

    fig, picks_list, titles_list, units_list, scalings_list, ax_list, \
        make_label = _set_psd_plot_params(raw.info, proj, picks, ax, area_mode)
    del ax
    if line_alpha is None:
        line_alpha = 1.0 if average else 0.75
    line_alpha = float(line_alpha)

    psd_list = list()
    ylabels = list()
    if n_fft is None:
        tmax = raw.times[-1] if not np.isfinite(tmax) else tmax
        n_fft = min(np.diff(raw.time_as_index([tmin, tmax]))[0] + 1, 2048)
    for ii, picks in enumerate(picks_list):
        ax = ax_list[ii]
        psds, freqs = psd_welch(raw, tmin=tmin, tmax=tmax, picks=picks,
                                fmin=fmin, fmax=fmax, proj=proj, n_fft=n_fft,
                                n_overlap=n_overlap, n_jobs=n_jobs,
                                reject_by_annotation=reject_by_annotation)

        ylabel = _convert_psds(psds, dB, estimate, scalings_list[ii],
                               units_list[ii],
                               [raw.ch_names[pi] for pi in picks])

        if average:
            psd_mean = np.mean(psds, axis=0)
            if area_mode == 'std':
                psd_std = np.std(psds, axis=0)
                hyp_limits = (psd_mean - psd_std, psd_mean + psd_std)
            elif area_mode == 'range':
                hyp_limits = (np.min(psds, axis=0), np.max(psds, axis=0))
            else:  # area_mode is None
                hyp_limits = None

            ax.plot(freqs, psd_mean, color=color, alpha=line_alpha,
                    linewidth=0.5)
            if hyp_limits is not None:
                ax.fill_between(freqs, hyp_limits[0], y2=hyp_limits[1],
                                color=color, alpha=area_alpha)
        else:
            psd_list.append(psds)

        if make_label:
            if ii == len(picks_list) - 1:
                ax.set_xlabel('Frequency (Hz)')
            ax.set_ylabel(ylabel)
            ax.set_title(titles_list[ii])
            ax.set_xlim(freqs[0], freqs[-1])

        ylabels.append(ylabel)

    for key, ls in zip(['lowpass', 'highpass', 'line_freq'],
                       ['--', '--', '-.']):
        if raw.info[key] is not None:
            for ax in ax_list:
                ax.axvline(raw.info[key], color='k', linestyle=ls, alpha=0.25,
                           linewidth=2, zorder=2)

    if not average:
        picks = np.concatenate(picks_list)

        psd_list = np.concatenate(psd_list)
        types = np.array([channel_type(raw.info, idx) for idx in picks])
        # Needed because the data does not match the info anymore.
        info = create_info([raw.ch_names[p] for p in picks], raw.info['sfreq'],
                           types)
        info['chs'] = [raw.info['chs'][p] for p in picks]
        valid_channel_types = ['mag', 'grad', 'eeg', 'seeg', 'eog', 'ecg',
                               'emg', 'dipole', 'gof', 'bio', 'ecog', 'hbo',
                               'hbr', 'misc']
        ch_types_used = list()
        for this_type in valid_channel_types:
            if this_type in types:
                ch_types_used.append(this_type)
        unit = ''
        units = {t: yl for t, yl in zip(ch_types_used, ylabels)}
        titles = {c: t for c, t in zip(ch_types_used, titles_list)}
        picks = np.arange(len(psd_list))
        if not spatial_colors:
            spatial_colors = color
        _plot_lines(psd_list, info, picks, fig, ax_list, spatial_colors,
                    unit, units=units, scalings=None, hline=None, gfp=False,
                    types=types, zorder='std', xlim=(freqs[0], freqs[-1]),
                    ylim=None, times=freqs, bad_ch_idx=[], titles=titles,
                    ch_types_used=ch_types_used, selectable=True, psd=True,
                    line_alpha=line_alpha)
    for ax in ax_list:
        ax.grid(True, linestyle=':')
        if xscale == 'log':
            ax.set(xscale='log')
            ax.set(xlim=[freqs[1] if freqs[0] == 0 else freqs[0], freqs[-1]])
            ax.get_xaxis().set_major_formatter(ScalarFormatter())
    if make_label:
        tight_layout(pad=0.1, h_pad=0.1, w_pad=0.1, fig=fig)
    plt_show(show)
    return fig