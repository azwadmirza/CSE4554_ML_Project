    def plot_rug(self, height, expand_margins, legend, **kws):

        for sub_vars, sub_data, in self.iter_data():

            ax = self._get_axes(sub_vars)

            kws.setdefault("linewidth", 1)

            if expand_margins:
                xmarg, ymarg = ax.margins()
                if "x" in self.variables:
                    ymarg += height * 2
                if "y" in self.variables:
                    xmarg += height * 2
                ax.margins(x=xmarg, y=ymarg)

            if "hue" in self.variables:
                kws.pop("c", None)
                kws.pop("color", None)

            if "x" in self.variables:
                self._plot_single_rug(sub_data, "x", height, ax, kws)
            if "y" in self.variables:
                self._plot_single_rug(sub_data, "y", height, ax, kws)

            # --- Finalize the plot
            self._add_axis_labels(ax)
            if "hue" in self.variables and legend:
                # TODO ideally i'd like the legend artist to look like a rug
                legend_artist = partial(mpl.lines.Line2D, [], [])
                self._add_legend(
                    ax, legend_artist, False, False, None, 1, {}, {},
                )