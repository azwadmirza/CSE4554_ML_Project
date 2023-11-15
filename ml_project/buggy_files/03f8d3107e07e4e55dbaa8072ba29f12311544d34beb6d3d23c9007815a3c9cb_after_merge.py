    def plot_bss_loadings(self, comp_ids=None, calibrate=True,
                          same_window=True, comp_label=None,
                          with_factors=False, cmap=plt.cm.gray,
                          no_nans=False, per_row=3, axes_decor='all',
                          title=None):
        """Plot loadings from blind source separation results. In case of 1D
        navigation axis, each loading line can be toggled on and off by
        clicking on their corresponding line in the legend.

        Parameters
        ----------

        comp_ids : None, int, or list (of ints)
            If `comp_ids` is ``None``, maps of all components will be
            returned. If it is an int, maps of components with ids from 0 to
            the given value will be returned. If `comp_ids` is a list of
            ints, maps of components with ids contained in the list will be
            returned.

        calibrate : bool
            if ``True``, calibrates plots where calibration is available
            from the axes_manager.  If ``False``, plots are in pixels/channels.

        same_window : bool
            If ``True``, plots each factor to the same window. They are
            not scaled. Default is ``True``.

        comp_label : str
            Will be deprecated in 2.0, please use `title` instead

        title : str
            Title of the plot.

        with_factors : bool
            If `True`, also returns figure(s) with the factors for the
            given `comp_ids`.

        cmap : :py:class:`~matplotlib.colors.Colormap`
            The colormap used for the factor image, or for peak
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.

        no_nans : bool
            If ``True``, removes ``NaN``'s from the loading plots.

        per_row : int
            The number of plots in each row, when the `same_window`
            parameter is ``True``.

        axes_decor : str or None, optional
            One of: ``'all'``, ``'ticks'``, ``'off'``, or ``None``
            Controls how the axes are displayed on each image;
            default is ``'all'``
            If ``'all'``, both ticks and axis labels will be shown
            If ``'ticks'``, no axis labels will be shown, but ticks/labels will
            If ``'off'``, all decorations and frame will be disabled
            If ``None``, no axis decorations will be shown, but ticks/frame will

        See also
        --------
        plot_bss_factors, plot_bss_results

        """
        if self.axes_manager.navigation_dimension > 2:
            raise NotImplementedError("This method cannot plot loadings of "
                                      "dimension higher than 2."
                                      "You can use "
                                      "`plot_bss_results` instead.")
        if self.learning_results.bss_loadings is None:
            raise RuntimeError("No learning results found. A "
                               "'blind_source_separation' needs to be "
                               "performed first.")
        if same_window is None:
            same_window = True
        title = _change_API_comp_label(title, comp_label)
        if title is None:
            title = self._get_plot_title('BSS loadings of',
                                         same_window)
        loadings = self.learning_results.bss_loadings.T
        if with_factors:
            factors = self.learning_results.bss_factors
        else:
            factors = None
        return self._plot_loadings(
            loadings,
            comp_ids=comp_ids,
            with_factors=with_factors,
            factors=factors,
            same_window=same_window,
            comp_label=title,
            cmap=cmap,
            no_nans=no_nans,
            per_row=per_row,
            axes_decor=axes_decor)