    def plot_bivariate_density(
        self,
        common_norm,
        fill,
        levels,
        thresh,
        color,
        legend,
        cbar,
        cbar_ax,
        cbar_kws,
        estimate_kws,
        **contour_kws,
    ):

        contour_kws = contour_kws.copy()

        estimator = KDE(**estimate_kws)

        if not set(self.variables) - {"x", "y"}:
            common_norm = False

        all_data = self.plot_data.dropna()

        # Loop through the subsets and estimate the KDEs
        densities, supports = {}, {}

        for sub_vars, sub_data in self.iter_data("hue", from_comp_data=True):

            # Extract the data points from this sub set and remove nulls
            sub_data = sub_data.dropna()
            observations = sub_data[["x", "y"]]

            # Extract the weights for this subset of observations
            if "weights" in self.variables:
                weights = sub_data["weights"]
            else:
                weights = None

            # Check that KDE will not error out
            variance = observations[["x", "y"]].var()
            if np.isclose(variance, 0).any() or variance.isna().any():
                msg = "Dataset has 0 variance; skipping density estimate."
                warnings.warn(msg, UserWarning)
                continue

            # Estimate the density of observations at this level
            observations = observations["x"], observations["y"]
            density, support = estimator(*observations, weights=weights)

            # Transform the support grid back to the original scale
            xx, yy = support
            if self._log_scaled("x"):
                xx = np.power(10, xx)
            if self._log_scaled("y"):
                yy = np.power(10, yy)
            support = xx, yy

            # Apply a scaling factor so that the integral over all subsets is 1
            if common_norm:
                density *= len(sub_data) / len(all_data)

            key = tuple(sub_vars.items())
            densities[key] = density
            supports[key] = support

        # Define a grid of iso-proportion levels
        if thresh is None:
            thresh = 0
        if isinstance(levels, Number):
            levels = np.linspace(thresh, 1, levels)
        else:
            if min(levels) < 0 or max(levels) > 1:
                raise ValueError("levels must be in [0, 1]")

        # Transform from iso-proportions to iso-densities
        if common_norm:
            common_levels = self._quantile_to_level(
                list(densities.values()), levels,
            )
            draw_levels = {k: common_levels for k in densities}
        else:
            draw_levels = {
                k: self._quantile_to_level(d, levels)
                for k, d in densities.items()
            }

        # Get a default single color from the attribute cycle
        if self.ax is None:
            default_color = "C0" if color is None else color
        else:
            scout, = self.ax.plot([], color=color)
            default_color = scout.get_color()
            scout.remove()

        # Define the coloring of the contours
        if "hue" in self.variables:
            for param in ["cmap", "colors"]:
                if param in contour_kws:
                    msg = f"{param} parameter ignored when using hue mapping."
                    warnings.warn(msg, UserWarning)
                    contour_kws.pop(param)
        else:

            # Work out a default coloring of the contours
            coloring_given = set(contour_kws) & {"cmap", "colors"}
            if fill and not coloring_given:
                cmap = self._cmap_from_color(default_color)
                contour_kws["cmap"] = cmap
            if not fill and not coloring_given:
                contour_kws["colors"] = [default_color]

            # Use our internal colormap lookup
            cmap = contour_kws.pop("cmap", None)
            if isinstance(cmap, str):
                cmap = color_palette(cmap, as_cmap=True)
            if cmap is not None:
                contour_kws["cmap"] = cmap

        # Loop through the subsets again and plot the data
        for sub_vars, _ in self.iter_data("hue"):

            if "hue" in sub_vars:
                color = self._hue_map(sub_vars["hue"])
                if fill:
                    contour_kws["cmap"] = self._cmap_from_color(color)
                else:
                    contour_kws["colors"] = [color]

            ax = self._get_axes(sub_vars)

            # Choose the function to plot with
            # TODO could add a pcolormesh based option as well
            # Which would look something like element="raster"
            if fill:
                contour_func = ax.contourf
            else:
                contour_func = ax.contour

            key = tuple(sub_vars.items())
            if key not in densities:
                continue
            density = densities[key]
            xx, yy = supports[key]

            label = contour_kws.pop("label", None)

            cset = contour_func(
                xx, yy, density,
                levels=draw_levels[key],
                **contour_kws,
            )

            if "hue" not in self.variables:
                cset.collections[0].set_label(label)

            # Add a color bar representing the contour heights
            # Note: this shows iso densities, not iso proportions
            # See more notes in histplot about how this could be improved
            if cbar:
                cbar_kws = {} if cbar_kws is None else cbar_kws
                ax.figure.colorbar(cset, cbar_ax, ax, **cbar_kws)

        # --- Finalize the plot
        ax = self.ax if self.ax is not None else self.facets.axes.flat[0]
        self._add_axis_labels(ax)

        if "hue" in self.variables and legend:

            # TODO if possible, I would like to move the contour
            # intensity information into the legend too and label the
            # iso proportions rather than the raw density values

            artist_kws = {}
            if fill:
                artist = partial(mpl.patches.Patch)
            else:
                artist = partial(mpl.lines.Line2D, [], [])

            ax_obj = self.ax if self.ax is not None else self.facets
            self._add_legend(
                ax_obj, artist, fill, False, "layer", 1, artist_kws, {},
            )