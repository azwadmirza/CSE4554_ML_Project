    def plot_image(self, picks=None, exclude='bads', unit=True, show=True,
                   clim=None, xlim='tight', proj=False, units=None,
                   scalings=None, titles=None, axes=None, cmap='RdBu_r'):
        """Plot evoked data as images

        Parameters
        ----------
        picks : array-like of int | None
            The indices of channels to plot. If None show all.
        exclude : list of str | 'bads'
            Channels names to exclude from being shown. If 'bads', the
            bad channels are excluded.
        unit : bool
            Scale plot with channel (SI) unit.
        show : bool
            Call pyplot.show() at the end or not.
        clim : dict
            clim for images. e.g. clim = dict(eeg=[-200e-6, 200e6])
            Valid keys are eeg, mag, grad
        xlim : 'tight' | tuple | None
            xlim for plots.
        proj : bool | 'interactive'
            If true SSP projections are applied before display. If
            'interactive', a check box for reversible selection of SSP
            projection vectors will be shown.
        units : dict | None
            The units of the channel types used for axes lables. If None,
            defaults to `dict(eeg='uV', grad='fT/cm', mag='fT')`.
        scalings : dict | None
            The scalings of the channel types to be applied for plotting.
            If None, defaults to `dict(eeg=1e6, grad=1e13, mag=1e15)`.
        titles : dict | None
            The titles associated with the channels. If None, defaults to
            `dict(eeg='EEG', grad='Gradiometers', mag='Magnetometers')`.
        axes : instance of Axes | list | None
            The axes to plot to. If list, the list must be a list of Axes of
            the same length as the number of channel types. If instance of
            Axes, there must be only one channel type plotted.
        cmap : matplotlib colormap | (colormap, bool) | 'interactive'
            Colormap. If tuple, the first value indicates the colormap to use
            and the second value is a boolean defining interactivity. In
            interactive mode the colors are adjustable by clicking and dragging
            the colorbar with left and right mouse button. Left mouse button
            moves the scale up and down and right mouse button adjusts the
            range. Hitting space bar resets the scale. Up and down arrows can
            be used to change the colormap. If 'interactive', translates to
            ('RdBu_r', True). Defaults to 'RdBu_r'.

        Returns
        -------
        fig : instance of matplotlib.figure.Figure
            Figure containing the images.
        """
        return plot_evoked_image(self, picks=picks, exclude=exclude, unit=unit,
                                 show=show, clim=clim, proj=proj, xlim=xlim,
                                 units=units, scalings=scalings,
                                 titles=titles, axes=axes, cmap=cmap)