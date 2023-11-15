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

        if homology_dimensions is None:
            _homology_dimensions = list(enumerate(self.homology_dimensions_))
        else:
            _homology_dimensions = []
            for dim in homology_dimensions:
                if dim not in self.homology_dimensions_:
                    raise ValueError(
                        f"All homology dimensions must be in "
                        f"self.homology_dimensions_ which is "
                        f"{self.homology_dimensions_}. {dim} is not.")
                else:
                    homology_dimensions_arr = np.array(
                        self.homology_dimensions_)
                    ix = np.flatnonzero(homology_dimensions_arr == dim)[0]
                    _homology_dimensions.append((ix, dim))

        layout = {
            "xaxis1": {
                "side": "bottom",
                "type": "linear",
                "ticks": "outside",
                "anchor": "y1",
                "showline": True,
                "zeroline": True,
                "showexponent": "all",
                "exponentformat": "e"
                },
            "yaxis1": {
                "side": "left",
                "type": "linear",
                "ticks": "outside",
                "anchor": "x1",
                "showline": True,
                "zeroline": True,
                "showexponent": "all",
                "exponentformat": "e"
                },
            "plot_bgcolor": "white",
            "title": f"Landscape representation of diagram {sample}"
            }

        Xt_sample = Xt[sample]
        for ix, dim in _homology_dimensions:
            layout_dim = layout.copy()
            layout_dim["title"] = "Persistence landscape for homology " + \
                                  "dimension {}".format(int(dim))
            fig = gobj.Figure(layout=layout_dim)
            fig.update_xaxes(zeroline=True, linewidth=1, linecolor="black",
                             mirror=False)
            fig.update_yaxes(zeroline=True, linewidth=1, linecolor="black",
                             mirror=False)

            n_layers = Xt_sample.shape[1]
            for layer in range(n_layers):
                fig.add_trace(gobj.Scatter(x=self.samplings_[dim],
                                           y=Xt_sample[ix, layer],
                                           mode="lines", showlegend=True,
                                           hoverinfo="none",
                                           name=f"Layer {layer + 1}"))

            # Update traces and layout according to user input
            if plotly_params:
                fig.update_traces(plotly_params.get("traces", None))
                fig.update_layout(plotly_params.get("layout", None))

            return fig