def plot_epochs_psd_topomap(epochs, bands=None, vmin=None, vmax=None,
                            tmin=None, tmax=None, proj=False,
                            bandwidth=None, adaptive=False, low_bias=True,
                            normalization='length', ch_type=None, layout=None,
                            cmap='RdBu_r', agg_fun=None, dB=False, n_jobs=1,
                            normalize=False, cbar_fmt='%0.3f',
                            outlines='head', show=True, verbose=None):
    """Plot the topomap of the power spectral density across epochs

    Parameters
    ----------
    epochs : instance of Epochs
        The epochs object
    bands : list of tuple | None
        The lower and upper frequency and the name for that band. If None,
        (default) expands to:

        bands = [(0, 4, 'Delta'), (4, 8, 'Theta'), (8, 12, 'Alpha'),
                 (12, 30, 'Beta'), (30, 45, 'Gamma')]

    vmin : float | callable | None
        The value specifying the lower bound of the color range.
        If None np.min(data) is used. If callable, the output equals
        vmin(data).
    vmax : float | callable | None
        The value specifying the upper bound of the color range.
        If None, the maximum absolute value is used. If callable, the output
        equals vmax(data). Defaults to None.
    tmin : float | None
        Start time to consider.
    tmax : float | None
        End time to consider.
    proj : bool
        Apply projection.
    bandwidth : float
        The bandwidth of the multi taper windowing function in Hz. The default
        value is a window half-bandwidth of 4 Hz.
    adaptive : bool
        Use adaptive weights to combine the tapered spectra into PSD
        (slow, use n_jobs >> 1 to speed up computation).
    low_bias : bool
        Only use tapers with more than 90% spectral concentration within
        bandwidth.
    normalization : str
        Either "full" or "length" (default). If "full", the PSD will
        be normalized by the sampling rate as well as the length of
        the signal (as in nitime).
    ch_type : 'mag' | 'grad' | 'planar1' | 'planar2' | 'eeg' | None
        The channel type to plot. For 'grad', the gradiometers are collected in
        pairs and the RMS for each pair is plotted. If None, then first
        available channel type from order given above is used. Defaults to
        None.
    layout : None | Layout
        Layout instance specifying sensor positions (does not need to
        be specified for Neuromag data). If possible, the correct layout
        file is inferred from the data; if no appropriate layout file was
        found, the layout is automatically generated from the sensor
        locations.
    cmap : matplotlib colormap
        Colormap. For magnetometers and eeg defaults to 'RdBu_r', else
        'Reds'.
    agg_fun : callable
        The function used to aggregate over frequencies.
        Defaults to np.sum. if normalize is True, else np.mean.
    dB : bool
        If True, transform data to decibels (with ``10 * np.log10(data)``)
        following the application of `agg_fun`. Only valid if normalize is
        False.
    n_jobs : int
        Number of jobs to run in parallel.
    normalize : bool
        If True, each band will be divided by the total power. Defaults to
        False.
    cbar_fmt : str
        The colorbar format. Defaults to '%0.3f'.
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
    show : bool
        Show figure if True.
    verbose : bool, str, int, or None
        If not None, override default verbose level (see mne.verbose).

    Returns
    -------
    fig : instance of matplotlib figure
        Figure distributing one image per channel across sensor topography.
    """
    from ..channels import _get_ch_type
    ch_type = _get_ch_type(epochs, ch_type)

    picks, pos, merge_grads, names, ch_type = _prepare_topo_plot(
        epochs, ch_type, layout)

    psds, freqs = psd_multitaper(epochs, tmin=tmin, tmax=tmax,
                                 bandwidth=bandwidth, adaptive=adaptive,
                                 low_bias=low_bias,
                                 normalization=normalization, picks=picks,
                                 proj=proj, n_jobs=n_jobs)
    psds = np.mean(psds, axis=0)

    if merge_grads:
        from ..channels.layout import _merge_grad_data
        psds = _merge_grad_data(psds)

    return plot_psds_topomap(
        psds=psds, freqs=freqs, pos=pos, agg_fun=agg_fun, vmin=vmin,
        vmax=vmax, bands=bands, cmap=cmap, dB=dB, normalize=normalize,
        cbar_fmt=cbar_fmt, outlines=outlines, show=show)