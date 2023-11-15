    def plot(self, Xt, sample=0, homology_dimensions=None, plotly_params=None):
        """Plot a sample from a collection of persistence landscapes arranged
        as in the output of :meth:`transform`. Include homology in multiple
        dimensions.

        Parameters
        ----------
        Xt : ndarray of shape (n_samples, n_homology_dimensions, n_layers, \
            n_bins
            Collection of persistence landscapes, such as returned by
            :meth:`transform`.

        sample : int, optional, default: ``0``
            Index of the sample in `Xt` to be plotted.

        homology_dimensions : list, tuple or None, optional, default: ``None``
            Homology dimensions for which the landscape should be plotted.
            ``None`` means plotting all dimensions present in
            :attr:`homology_dimensions_`.

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
                "side": "bottom",
                "anchor": "y1",
                **layout_axes_common
                },
            "yaxis1": {
                "side": "left",
                "anchor": "x1",
                **layout_axes_common
                },
            "plot_bgcolor": "white",
            }

        Xt_sample = Xt[sample]
        n_layers = Xt_sample.shape[1]
        subplot_titles = [f"H{dim}" for _, dim in homology_dimensions_mapping]
        fig = make_subplots(rows=len(homology_dimensions_mapping), cols=1,
                            subplot_titles=subplot_titles)
        has_many_homology_dim = len(homology_dimensions_mapping) - 1
        for i, (inv_idx, dim) in enumerate(homology_dimensions_mapping):
            hom_dim_str = \
                f" ({subplot_titles[i]})" if has_many_homology_dim else ""
            for layer in range(n_layers):
                fig.add_trace(
                    Scatter(x=self.samplings_[dim],
                            y=Xt_sample[inv_idx, layer],
                            mode="lines",
                            showlegend=True,
                            hoverinfo="none",
                            name=f"Layer {layer + 1}{hom_dim_str}"),
                    row=i + 1,
                    col=1
                    )

        fig.update_layout(
            title_text=f"Landscape representations of diagram {sample}",
            **layout.copy()
            )

        # Update traces and layout according to user input
        if plotly_params:
            fig.update_traces(plotly_params.get("traces", None))
            fig.update_layout(plotly_params.get("layout", None))

        return fig