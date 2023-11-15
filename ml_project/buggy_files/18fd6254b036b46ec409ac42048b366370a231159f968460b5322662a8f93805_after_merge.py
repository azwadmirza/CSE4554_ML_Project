    def map_diag(self, func, **kwargs):
        """Plot with a univariate function on each diagonal subplot.

        Parameters
        ----------
        func : callable plotting function
            Must take an x array as a positional argument and draw onto the
            "currently active" matplotlib Axes. Also needs to accept kwargs
            called ``color`` and  ``label``.

        """
        # Add special diagonal axes for the univariate plot
        if self.diag_axes is None:
            diag_vars = []
            diag_axes = []
            for i, y_var in enumerate(self.y_vars):
                for j, x_var in enumerate(self.x_vars):
                    if x_var == y_var:

                        # Make the density axes
                        diag_vars.append(x_var)
                        ax = self.axes[i, j]
                        diag_ax = ax.twinx()
                        diag_ax.set_axis_off()
                        diag_axes.append(diag_ax)

                        # Work around matplotlib bug
                        # https://github.com/matplotlib/matplotlib/issues/15188
                        if not plt.rcParams.get("ytick.left", True):
                            for tick in ax.yaxis.majorTicks:
                                tick.tick1line.set_visible(False)

                        # Remove main y axis from density axes in a corner plot
                        if self._corner:
                            ax.yaxis.set_visible(False)
                            if self._despine:
                                utils.despine(ax=ax, left=True)
                            # TODO add optional density ticks (on the right)
                            # when drawing a corner plot?

            if self.diag_sharey and diag_axes:
                # This may change in future matplotlibs
                # See https://github.com/matplotlib/matplotlib/pull/9923
                group = diag_axes[0].get_shared_y_axes()
                for ax in diag_axes[1:]:
                    group.join(ax, diag_axes[0])

            self.diag_vars = np.array(diag_vars, np.object_)
            self.diag_axes = np.array(diag_axes, np.object_)

        if "hue" not in signature(func).parameters:
            return self._map_diag_iter_hue(func, **kwargs)

        # Loop over diagonal variables and axes, making one plot in each
        for var, ax in zip(self.diag_vars, self.diag_axes):

            plt.sca(ax)
            plot_kwargs = kwargs.copy()

            vector = self.data[var]
            if self._hue_var is not None:
                hue = self.data[self._hue_var]
            else:
                hue = None

            if self._dropna:
                not_na = vector.notna()
                if hue is not None:
                    not_na &= hue.notna()
                vector = vector[not_na]
                if hue is not None:
                    hue = hue[not_na]

            plot_kwargs.setdefault("hue", hue)
            plot_kwargs.setdefault("hue_order", self._hue_order)
            plot_kwargs.setdefault("palette", self._orig_palette)
            func(x=vector, **plot_kwargs)
            self._clean_axis(ax)

        self._add_axis_labels()
        return self