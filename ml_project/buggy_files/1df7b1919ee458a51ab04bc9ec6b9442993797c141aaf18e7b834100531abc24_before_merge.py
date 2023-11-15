    def plot_decomposition_loadings(self,
                                    comp_ids=None,
                                    calibrate=True,
                                    same_window=True,
                                    comp_label=None,
                                    with_factors=False,
                                    cmap=plt.cm.gray,
                                    no_nans=False,
                                    per_row=3,
                                    axes_decor='all',
                                    title=None):
        """Plot loadings from a decomposition. In case of 1D navigation axis,
        each loading line can be toggled on and off by clicking on the legended
        line.

        Parameters
        ----------

        comp_ids : None, int, or list (of ints)
            If `comp_ids` is ``None``, maps of all components will be
            returned if the `output_dimension` was defined when executing
            :py:meth:`~hyperspy.learn.mva.MVA.decomposition`.
            Otherwise it raises a :py:exc:`ValueError`.
            If `comp_ids` is an int, maps of components with ids from 0 to
            the given value will be returned. If `comp_ids` is a list of
            ints, maps of components with ids contained in the list will be
            returned.

        calibrate : bool
            if ``True``, calibrates plots where calibration is available
            from the axes_manager. If ``False``, plots are in pixels/channels.

        same_window : bool
            if ``True``, plots each factor to the same window. They are
            not scaled. Default is ``True``.

        title : str
            Title of the plot.

        with_factors : bool
            If ``True``, also returns figure(s) with the factors for the
            given comp_ids.

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
            Controls how the axes are displayed on each image; default is
            ``'all'``
            If ``'all'``, both ticks and axis labels will be shown.
            If ``'ticks'``, no axis labels will be shown, but ticks/labels will.
            If ``'off'``, all decorations and frame will be disabled.
            If ``None``, no axis decorations will be shown, but ticks/frame
            will.

        See also
        --------
        plot_decomposition_factors, plot_decomposition_results

        """
        if self.axes_manager.navigation_dimension > 2:
            raise NotImplementedError("This method cannot plot loadings of "
                                      "dimension higher than 2."
                                      "You can use "
                                      "`plot_decomposition_results` instead.")
        if same_window is None:
            same_window = True
        loadings = self.learning_results.loadings.T
        if with_factors:
            factors = self.learning_results.factors
        else:
            factors = None

        if comp_ids is None:
            if self.learning_results.output_dimension:
                comp_ids = self.learning_results.output_dimension
            else:
                raise ValueError(
                    "Please provide the number of components to plot via the "
                    "`comp_ids` argument")
        title = _change_API_comp_label(title, comp_label)
        if title is None:
            title = self._get_plot_title('Decomposition loadings of',
                                         same_window)

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