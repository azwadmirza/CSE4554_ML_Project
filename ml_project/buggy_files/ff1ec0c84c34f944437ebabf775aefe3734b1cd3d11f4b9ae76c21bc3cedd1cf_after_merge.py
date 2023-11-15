    def plot_decomposition_factors(self,
                                   comp_ids=None,
                                   calibrate=True,
                                   same_window=True,
                                   comp_label=None,
                                   cmap=plt.cm.gray,
                                   per_row=3,
                                   title=None):
        """Plot factors from a decomposition. In case of 1D signal axis, each
        factors line can be toggled on and off by clicking on their
        corresponding line in the legend.

        Parameters
        ----------

        comp_ids : None, int, or list (of ints)
            If `comp_ids` is ``None``, maps of all components will be
            returned if the `output_dimension` was defined when executing
            :py:meth:`~hyperspy.learn.mva.MVA.decomposition`. Otherwise it
            raises a :py:exc:`ValueError`.
            If `comp_ids` is an int, maps of components with ids from 0 to
            the given value will be returned. If `comp_ids` is a list of
            ints, maps of components with ids contained in the list will be
            returned.

        calibrate : bool
            If ``True``, calibrates plots where calibration is available
            from the axes_manager.  If ``False``, plots are in pixels/channels.

        same_window : bool
            If ``True``, plots each factor to the same window.  They are
            not scaled. Default is ``True``.

        title : str
            Title of the plot.

        cmap : :py:class:`~matplotlib.colors.Colormap`
            The colormap used for the factor image, or for peak
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.

        per_row : int
            The number of plots in each row, when the `same_window`
            parameter is ``True``.

        See also
        --------
        plot_decomposition_loadings, plot_decomposition_results

        """
        if self.axes_manager.signal_dimension > 2:
            raise NotImplementedError("This method cannot plot factors of "
                                      "signals of dimension higher than 2."
                                      "You can use "
                                      "`plot_decomposition_results` instead.")
        if self.learning_results.factors is None:
            raise RuntimeError("No learning results found. A 'decomposition' "
                               "needs to be performed first.")
        if same_window is None:
            same_window = True
        factors = self.learning_results.factors
        if comp_ids is None:
            if self.learning_results.output_dimension:
                comp_ids = self.learning_results.output_dimension
            else:
                raise ValueError(
                    "Please provide the number of components to plot via the "
                    "`comp_ids` argument")
        title = _change_API_comp_label(title, comp_label)
        if title is None:
            title = self._get_plot_title('Decomposition factors of',
                                         same_window)

        return self._plot_factors_or_pchars(factors,
                                            comp_ids=comp_ids,
                                            calibrate=calibrate,
                                            same_window=same_window,
                                            comp_label=title,
                                            cmap=cmap,
                                            per_row=per_row)