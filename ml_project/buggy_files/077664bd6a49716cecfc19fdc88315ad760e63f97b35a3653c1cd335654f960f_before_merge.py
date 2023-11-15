    def plot(self, picks=None, baseline=None, mode='mean', tmin=None,
             tmax=None, fmin=None, fmax=None, vmin=None, vmax=None,
             cmap='RdBu_r', dB=False, colorbar=True, show=True,
             title=None, axes=None, layout=None, verbose=None):
        """Plot TFRs in a topography with images

        Parameters
        ----------
        picks : array-like of int | None
            The indices of the channels to plot.
        baseline : None (default) or tuple of length 2
            The time interval to apply baseline correction.
            If None do not apply it. If baseline is (a, b)
            the interval is between "a (s)" and "b (s)".
            If a is None the beginning of the data is used
            and if b is None then b is set to the end of the interval.
            If baseline is equal ot (None, None) all the time
            interval is used.
        mode : None | 'logratio' | 'ratio' | 'zscore' | 'mean' | 'percent'
            Do baseline correction with ratio (power is divided by mean
            power during baseline) or zscore (power is divided by standard
            deviation of power during baseline after subtracting the mean,
            power = [power - mean(power_baseline)] / std(power_baseline)).
            If None no baseline correction is applied.
        tmin : None | float
            The first time instant to display. If None the first time point
            available is used.
        tmax : None | float
            The last time instant to display. If None the last time point
            available is used.
        fmin : None | float
            The first frequency to display. If None the first frequency
            available is used.
        fmax : None | float
            The last frequency to display. If None the last frequency
            available is used.
        vmin : float | None
            The mininum value an the color scale. If vmin is None, the data
            minimum value is used.
        vmax : float | None
            The maxinum value an the color scale. If vmax is None, the data
            maximum value is used.
        cmap : matplotlib colormap | str
            The colormap to use. Defaults to 'RdBu_r'.
        dB : bool
            If True, 20*log10 is applied to the data to get dB.
        colorbar : bool
            If true, colorbar will be added to the plot. For user defined axes,
            the colorbar cannot be drawn. Defaults to True.
        show : bool
            Call pyplot.show() at the end.
        title : str | None
            String for title. Defaults to None (blank/no title).
        axes : instance of Axes | list | None
            The axes to plot to. If list, the list must be a list of Axes of
            the same length as the number of channels. If instance of Axes,
            there must be only one channel plotted.
        layout : Layout | None
            Layout instance specifying sensor positions. Used for interactive
            plotting of topographies on rectangle selection. If possible, the
            correct layout is inferred from the data.
        verbose : bool, str, int, or None
            If not None, override default verbose level (see mne.verbose).

        Returns
        -------
        fig : matplotlib.figure.Figure
            The figure containing the topography.
        """
        from ..viz.topo import _imshow_tfr
        import matplotlib.pyplot as plt
        times, freqs = self.times.copy(), self.freqs.copy()
        info = self.info
        data = self.data

        n_picks = len(picks)
        info, data, picks = _prepare_picks(info, data, picks)
        data = data[picks]

        data, times, freqs, vmin, vmax = \
            _preproc_tfr(data, times, freqs, tmin, tmax, fmin, fmax, mode,
                         baseline, vmin, vmax, dB, info['sfreq'])

        tmin, tmax = times[0], times[-1]
        if isinstance(axes, plt.Axes):
            axes = [axes]
        if isinstance(axes, list) or isinstance(axes, np.ndarray):
            if len(axes) != n_picks:
                raise RuntimeError('There must be an axes for each picked '
                                   'channel.')

        for idx in range(len(data)):
            if axes is None:
                fig = plt.figure()
                ax = fig.add_subplot(111)
            else:
                ax = axes[idx]
                fig = ax.get_figure()
            onselect_callback = partial(self._onselect, baseline=baseline,
                                        mode=mode, layout=layout)
            _imshow_tfr(ax, 0, tmin, tmax, vmin, vmax, onselect_callback,
                        ylim=None, tfr=data[idx: idx + 1], freq=freqs,
                        x_label='Time (ms)', y_label='Frequency (Hz)',
                        colorbar=colorbar, picker=False, cmap=cmap)
            if title:
                fig.suptitle(title)
            colorbar = False  # only one colorbar for multiple axes
        plt_show(show)
        return fig