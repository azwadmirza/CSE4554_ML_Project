    def plot_psd_topomap(self, bands=None, vmin=None, vmax=None, proj=False,
                         bandwidth=None, adaptive=False, low_bias=True,
                         normalization='length', ch_type=None,
                         layout=None, cmap='RdBu_r', agg_fun=None, dB=True,
                         n_jobs=1, normalize=False, cbar_fmt='%0.3f',
                         outlines='head', show=True, verbose=None):
        """Plot the topomap of the power spectral density across epochs

        Parameters
        ----------
        bands : list of tuple | None
            The lower and upper frequency and the name for that band. If None,
            (default) expands to:

            bands = [(0, 4, 'Delta'), (4, 8, 'Theta'), (8, 12, 'Alpha'),
                     (12, 30, 'Beta'), (30, 45, 'Gamma')]

        vmin : float | callable | None
            The value specifying the lower bound of the color range.
            If None, and vmax is None, -vmax is used. Else np.min(data).
            If callable, the output equals vmin(data).
        vmax : float | callable | None
            The value specifying the upper bound of the color range.
            If None, the maximum absolute value is used. If callable, the
            output equals vmax(data). Defaults to None.
        proj : bool
            Apply projection.
        bandwidth : float
            The bandwidth of the multi taper windowing function in Hz.
            The default value is a window half-bandwidth of 4 Hz.
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
        ch_type : {None, 'mag', 'grad', 'planar1', 'planar2', 'eeg'}
            The channel type to plot. For 'grad', the gradiometers are
            collected in
            pairs and the RMS for each pair is plotted. If None, defaults to
            'mag' if MEG data are present and to 'eeg' if only EEG data are
            present.
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
            following the application of `agg_fun`. Only valid if normalize
            is False.
        n_jobs : int
            Number of jobs to run in parallel.
        normalize : bool
            If True, each band will be divided by the total power. Defaults to
            False.
        cbar_fmt : str
            The colorbar format. Defaults to '%0.3f'.
        outlines : 'head' | 'skirt' | dict | None
            The outlines to be drawn. If 'head', the default head scheme will
            be drawn. If 'skirt' the head scheme will be drawn, but sensors are
            allowed to be plotted outside of the head circle. If dict, each key
            refers to a tuple of x and y positions, the values in 'mask_pos'
            will serve as image mask, and the 'autoshrink' (bool) field will
            trigger automated shrinking of the positions due to points outside
            the outline. Alternatively, a matplotlib patch object can be passed
            for advanced masking options, either directly or as a function that
            returns patches (required for multi-axis plots). If None, nothing
            will be drawn. Defaults to 'head'.
        show : bool
            Show figure if True.
        verbose : bool, str, int, or None
            If not None, override default verbose level (see mne.verbose).

        Returns
        -------
        fig : instance of matplotlib figure
            Figure distributing one image per channel across sensor topography.
        """
        return plot_epochs_psd_topomap(
            self, bands=bands, vmin=vmin, vmax=vmax, proj=proj,
            bandwidth=bandwidth, adaptive=adaptive,
            low_bias=low_bias, normalization=normalization,
            ch_type=ch_type, layout=layout, cmap=cmap,
            agg_fun=agg_fun, dB=dB, n_jobs=n_jobs, normalize=normalize,
            cbar_fmt=cbar_fmt, outlines=outlines, show=show, verbose=None)