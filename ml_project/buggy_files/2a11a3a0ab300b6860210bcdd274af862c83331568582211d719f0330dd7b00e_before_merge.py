    def plot_bss_factors(self, comp_ids=None, calibrate=True,
                         same_window=True, comp_label=None,
                         per_row=3, title=None):
        """Plot factors from blind source separation results. In case of 1D
        signal axis, each factors line can be toggled on and off by clicking
        on their corresponding line in the legend.

        Parameters
        ----------

        comp_ids : None, int, or list (of ints)
            If `comp_ids` is ``None``, maps of all components will be
            returned. If it is an int, maps of components with ids from 0 to
            the given value will be returned. If `comp_ids` is a list of
            ints, maps of components with ids contained in the list will be
            returned.

        calibrate : bool
            If ``True``, calibrates plots where calibration is available
            from the axes_manager.  If ``False``, plots are in pixels/channels.

        same_window : bool
            if ``True``, plots each factor to the same window.  They are
            not scaled. Default is ``True``.

        comp_label : str
            Will be deprecated in 2.0, please use `title` instead

        title : str
            Title of the plot.

        per_row : int
            The number of plots in each row, when the `same_window`
            parameter is ``True``.

        See also
        --------
        plot_bss_loadings, plot_bss_results

        """
        if self.axes_manager.signal_dimension > 2:
            raise NotImplementedError("This method cannot plot factors of "
                                      "signals of dimension higher than 2."
                                      "You can use "
                                      "`plot_decomposition_results` instead.")

        if same_window is None:
            same_window = True
        factors = self.learning_results.bss_factors
        title = _change_API_comp_label(title, comp_label)
        if title is None:
            title = self._get_plot_title('BSS factors of', same_window)

        return self._plot_factors_or_pchars(factors,
                                            comp_ids=comp_ids,
                                            calibrate=calibrate,
                                            same_window=same_window,
                                            comp_label=title,
                                            per_row=per_row)