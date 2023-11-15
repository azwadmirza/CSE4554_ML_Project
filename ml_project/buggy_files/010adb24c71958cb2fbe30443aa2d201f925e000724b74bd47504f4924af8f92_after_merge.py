    def plot(self, Xt, sample=0, homology_dimension_idx=0, colorscale="blues",
             plotly_params=None):
        """Plot a single channel -– corresponding to a given homology
        dimension -– in a sample from a collection of persistence images.

        Parameters
        ----------
        Xt : ndarray of shape (n_samples, n_homology_dimensions, n_bins, \
            n_bins)
            Collection of multi-channel raster images, such as returned by
            :meth:`transform`.

        sample : int, optional, default: ``0``
            Index of the sample in `Xt` to be selected.

        homology_dimension_idx : int, optional, default: ``0``
            Index of the channel in the selected sample to be plotted. If `Xt`
            is the result of a call to :meth:`transform` and this index is i,
            the plot corresponds to the homology dimension given by the i-th
            entry in :attr:`homology_dimensions_`.

        colorscale : str, optional, default: ``"blues"``
            Color scale to be used in the heat map. Can be anything allowed by
            :class:`plotly.graph_objects.Heatmap`.

        plotly_params : dict or None, optional, default: ``None``
            Custom parameters to configure the plotly figure. Allowed keys are
            ``"trace"`` and ``"layout"``, and the corresponding values should
            be dictionaries containing keyword arguments as would be fed to the
            :meth:`update_traces` and :meth:`update_layout` methods of
            :class:`plotly.graph_objects.Figure`.

        Returns
        -------
        fig : :class:`plotly.graph_objects.Figure` object
            Plotly figure.

        """
        check_is_fitted(self)
        homology_dimension = self.homology_dimensions_[homology_dimension_idx]
        if homology_dimension != np.inf:
            homology_dimension = int(homology_dimension)
        samplings_x, samplings_y = self.samplings_[homology_dimension]
        return plot_heatmap(
            Xt[sample][homology_dimension_idx],
            x=samplings_x,
            y=samplings_y[::-1],
            colorscale=colorscale,
            origin="lower",
            title=f"Persistence image representation of diagram {sample} in "
                  f"homology dimension {homology_dimension}",
            plotly_params=plotly_params
            )