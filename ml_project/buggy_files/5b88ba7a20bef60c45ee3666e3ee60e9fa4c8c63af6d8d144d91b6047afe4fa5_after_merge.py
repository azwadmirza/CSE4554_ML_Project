    def plot_topomap(self, times="auto", ch_type=None, layout=None, vmin=None,
                     vmax=None, cmap=None, sensors=True, colorbar=True,
                     scale=None, scale_time=1e3, unit=None, res=64, size=1,
                     cbar_fmt="%3.1f", time_format='%01d ms', proj=False,
                     show=True, show_names=False, title=None, mask=None,
                     mask_params=None, outlines='head', contours=6,
                     image_interp='bilinear', average=None, head_pos=None,
                     axes=None):
        """Plot topographic maps of specific time points

        Parameters
        ----------
        times : float | array of floats | "auto" | "peaks".
            The time point(s) to plot. If "auto", the number of ``axes``
            determines the amount of time point(s). If ``axes`` is also None,
            10 topographies will be shown with a regular time spacing between
            the first and last time instant. If "peaks", finds time points
            automatically by checking for local maxima in Global Field Power.
        ch_type : 'mag' | 'grad' | 'planar1' | 'planar2' | 'eeg' | None
            The channel type to plot. For 'grad', the gradiometers are collec-
            ted in pairs and the RMS for each pair is plotted.
            If None, then first available channel type from order given
            above is used. Defaults to None.
        layout : None | Layout
            Layout instance specifying sensor positions (does not need to
            be specified for Neuromag data). If possible, the correct
            layout file is inferred from the data; if no appropriate layout
            file was found, the layout is automatically generated from the
            sensor locations.
        vmin : float | callable
            The value specfying the lower bound of the color range.
            If None, and vmax is None, -vmax is used. Else np.min(data).
            If callable, the output equals vmin(data).
        vmax : float | callable
            The value specfying the upper bound of the color range.
            If None, the maximum absolute value is used. If vmin is None,
            but vmax is not, defaults to np.max(data).
            If callable, the output equals vmax(data).
        cmap : matplotlib colormap | (colormap, bool) | 'interactive' | None
            Colormap to use. If tuple, the first value indicates the colormap
            to use and the second value is a boolean defining interactivity. In
            interactive mode the colors are adjustable by clicking and dragging
            the colorbar with left and right mouse button. Left mouse button
            moves the scale up and down and right mouse button adjusts the
            range. Hitting space bar resets the range. Up and down arrows can
            be used to change the colormap. If None (default), 'Reds' is used
            for all positive data, otherwise defaults to 'RdBu_r'. If
            'interactive', translates to (None, True).

            .. warning::  Interactive mode works smoothly only for a small
                amount of topomaps.

        sensors : bool | str
            Add markers for sensor locations to the plot. Accepts matplotlib
            plot format string (e.g., 'r+' for red plusses). If True, a circle
            will be used (via .add_artist). Defaults to True.
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
        size : scalar
            Side length of the topomaps in inches (only applies when plotting
            multiple topomaps at a time).
        cbar_fmt : str
            String format for colorbar values.
        time_format : str
            String format for topomap values. Defaults to ``"%01d ms"``.
        proj : bool | 'interactive'
            If true SSP projections are applied before display. If
            'interactive', a check box for reversible selection of SSP
            projection vectors will be shown.
        show : bool
            Call pyplot.show() at the end.
        show_names : bool | callable
            If True, show channel names on top of the map. If a callable is
            passed, channel names will be formatted using the callable; e.g.,
            to delete the prefix 'MEG ' from all channel names, pass the
            function
            lambda x: x.replace('MEG ', ''). If `mask` is not None, only
            significant sensors will be shown.
        title : str | None
            Title. If None (default), no title is displayed.
        mask : ndarray of bool, shape (n_channels, n_times) | None
            The channels to be marked as significant at a given time point.
            Indices set to `True` will be considered. Defaults to None.
        mask_params : dict | None
            Additional plotting parameters for plotting significant sensors.
            Default (None) equals:
            ``dict(marker='o', markerfacecolor='w', markeredgecolor='k',
            linewidth=0, markersize=4)``.
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
        contours : int | False | None
            The number of contour lines to draw. If 0, no contours will be
            drawn.
        image_interp : str
            The image interpolation to be used. All matplotlib options are
            accepted.
        average : float | None
            The time window around a given time to be used for averaging
            (seconds). For example, 0.01 would translate into window that
            starts 5 ms before and ends 5 ms after a given time point.
            Defaults to None, which means no averaging.
        head_pos : dict | None
            If None (default), the sensors are positioned such that they span
            the head circle. If dict, can have entries 'center' (tuple) and
            'scale' (tuple) for what the center and scale of the head should be
            relative to the electrode locations.
        axes : instance of Axes | list | None
            The axes to plot to. If list, the list must be a list of Axes of
            the same length as ``times`` (unless ``times`` is None). If
            instance of Axes, ``times`` must be a float or a list of one float.
            Defaults to None.

        Returns
        -------
        fig : instance of matplotlib.figure.Figure
            Images of evoked responses at sensor locations
        """
        return plot_evoked_topomap(self, times=times, ch_type=ch_type,
                                   layout=layout, vmin=vmin, vmax=vmax,
                                   cmap=cmap, sensors=sensors,
                                   colorbar=colorbar, scale=scale,
                                   scale_time=scale_time, unit=unit, res=res,
                                   proj=proj, size=size, cbar_fmt=cbar_fmt,
                                   time_format=time_format, show=show,
                                   show_names=show_names, title=title,
                                   mask=mask, mask_params=mask_params,
                                   outlines=outlines, contours=contours,
                                   image_interp=image_interp, average=average,
                                   head_pos=head_pos, axes=axes)