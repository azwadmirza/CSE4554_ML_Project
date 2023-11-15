    def plot(self, Xt, sample=0, homology_dimensions=None, plotly_params=None):
        """Plot a sample from a collection of Betti curves arranged as in
        the output of :meth:`transform`. Include homology in multiple
        dimensions.

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
                "title": "Filtration parameter",
                "side": "bottom",
                "type": "linear",
                "ticks": "outside",
                "anchor": "x1",
                "showline": True,
                "zeroline": True,
                "showexponent": "all",
                "exponentformat": "e"
                },
            "yaxis1": {
                "title": "Betti number",
                "side": "left",
                "type": "linear",
                "ticks": "outside",
                "anchor": "y1",
                "showline": True,
                "zeroline": True,
                "showexponent": "all",
                "exponentformat": "e"
                },
            "plot_bgcolor": "white",
            "title": f"Betti curves from diagram {sample}"
            }

        fig = gobj.Figure(layout=layout)
        fig.update_xaxes(zeroline=True, linewidth=1, linecolor="black",
                         mirror=False)
        fig.update_yaxes(zeroline=True, linewidth=1, linecolor="black",
                         mirror=False)

        for ix, dim in _homology_dimensions:
            fig.add_trace(gobj.Scatter(x=self.samplings_[dim],
                                       y=Xt[sample][ix],
                                       mode="lines", showlegend=True,
                                       name=f"H{int(dim)}"))

        # Update traces and layout according to user input
        if plotly_params:
            fig.update_traces(plotly_params.get("traces", None))
            fig.update_layout(plotly_params.get("layout", None))

        return fig