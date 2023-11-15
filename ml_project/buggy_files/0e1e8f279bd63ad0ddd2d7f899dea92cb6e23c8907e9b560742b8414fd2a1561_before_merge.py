    def plot_topo(self, picks=None, baseline=None, mode='mean', tmin=None,
                  tmax=None, fmin=None, fmax=None, vmin=None, vmax=None,
                  layout=None, cmap='RdBu_r', title=None, dB=False,
                  colorbar=True, layout_scale=0.945, show=True,
                  border='none', fig_facecolor='k', font_color='w'):
        """Plot TFRs in a topography with images

        Parameters
        ----------
        picks : array-like of int | None
            The indices of the channels to plot. If None all available
            channels are displayed.
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
        layout : Layout | None
            Layout instance specifying sensor positions. If possible, the
            correct layout is inferred from the data.
        cmap : matplotlib colormap | str
            The colormap to use. Defaults to 'RdBu_r'.
        title : str
            Title of the figure.
        dB : bool
            If True, 20*log10 is applied to the data to get dB.
        colorbar : bool
            If true, colorbar will be added to the plot
        layout_scale : float
            Scaling factor for adjusting the relative size of the layout
            on the canvas.
        show : bool
            Call pyplot.show() at the end.
        border : str
            matplotlib borders style to be used for each sensor plot.
        fig_facecolor : str | obj
            The figure face color. Defaults to black.
        font_color: str | obj
            The color of tick labels in the colorbar. Defaults to white.

        Returns
        -------
        fig : matplotlib.figure.Figure
            The figure containing the topography.
        """
        from ..viz.topo import _imshow_tfr, _plot_topo, _imshow_tfr_unified
        times = self.times.copy()
        freqs = self.freqs
        data = self.data
        info = self.info

        info, data, picks = _prepare_picks(info, data, picks)
        data = data[picks]

        data, times, freqs, vmin, vmax = \
            _preproc_tfr(data, times, freqs, tmin, tmax, fmin, fmax,
                         mode, baseline, vmin, vmax, dB, info['sfreq'])

        if layout is None:
            from mne import find_layout
            layout = find_layout(self.info)
        onselect_callback = partial(self._onselect, baseline=baseline,
                                    mode=mode, layout=layout)

        click_fun = partial(_imshow_tfr, tfr=data, freq=freqs, cmap=cmap,
                            onselect=onselect_callback)
        imshow = partial(_imshow_tfr_unified, tfr=data, freq=freqs, cmap=cmap,
                         onselect=onselect_callback)

        fig = _plot_topo(info=info, times=times, show_func=imshow,
                         click_func=click_fun, layout=layout,
                         colorbar=colorbar, vmin=vmin, vmax=vmax, cmap=cmap,
                         layout_scale=layout_scale, title=title, border=border,
                         x_label='Time (ms)', y_label='Frequency (Hz)',
                         fig_facecolor=fig_facecolor, font_color=font_color,
                         unified=True, img=True)
        plt_show(show)
        return fig