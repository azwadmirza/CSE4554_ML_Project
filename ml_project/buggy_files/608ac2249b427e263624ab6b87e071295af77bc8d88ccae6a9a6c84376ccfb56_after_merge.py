    def plot(self, Xt, sample=0, homology_dimensions=None, plotly_params=None):
        """Plot a sample from a collection of Betti curves arranged as in the
        output of :meth:`transform`. Include homology in multiple dimensions.

        Parameters
        ----------
        Xt : ndarray of shape (n_samples, n_homology_dimensions, n_bins)
            Collection of Betti curves, such as returned by :meth:`transform`.

        sample : int, optional, default: ``0``
            Index of the sample in `Xt` to be plotted.

        homology_dimensions : list, tuple or None, optional, default: ``None``
            Which homology dimensions to include in the plot. ``None`` means
            plotting all dimensions present in :attr:`homology_dimensions_`.

        plotly_params : dict or None, optional, default: ``None``
            Custom parameters to configure the plotly figure. Allowed keys are
            ``"traces"`` and ``"layout"``, and the corresponding values should
            be dictionaries containing keyword arguments as would be fed to the
            :meth:`update_traces` and :meth:`update_layout` methods of
            :class:`plotly.graph_objects.Figure`.

        Returns
        -------
        fig : :class:`plotly.graph_objects.Figure` object
            Plotly figure.

        """
        check_is_fitted(self)

        homology_dimensions_mapping = _make_homology_dimensions_mapping(
            homology_dimensions, self.homology_dimensions_
            )

        layout_axes_common = {
            "type": "linear",
            "ticks": "outside",
            "showline": True,
            "zeroline": True,
            "linewidth": 1,
            "linecolor": "black",
            "mirror": False,
            "showexponent": "all",
            "exponentformat": "e"
            }
        layout = {
            "xaxis1": {
                "title": "Filtration parameter",
                "side": "bottom",
                "anchor": "y1",
                **layout_axes_common
                },
            "yaxis1": {
                "title": "Betti number",
                "side": "left",
                "anchor": "x1",
                **layout_axes_common
                },
            "plot_bgcolor": "white",
            "title": f"Betti curves from diagram {sample}"
            }

        fig = Figure(layout=layout)

        for ix, dim in homology_dimensions_mapping:
            fig.add_trace(Scatter(x=self.samplings_[dim],
                                  y=Xt[sample][ix],
                                  mode="lines",
                                  showlegend=True,
                                  name=f"H{dim}"))

        # Update traces and layout according to user input
        if plotly_params:
            fig.update_traces(plotly_params.get("traces", None))
            fig.update_layout(plotly_params.get("layout", None))

        return fig