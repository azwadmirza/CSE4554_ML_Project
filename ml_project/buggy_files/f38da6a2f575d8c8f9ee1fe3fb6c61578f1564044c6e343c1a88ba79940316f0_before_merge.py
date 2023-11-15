    def _make_plot(self):
        # this is slightly deceptive
        x = self._get_xticks()

        plotf = self._get_plot_function()

        for i, (label, y) in enumerate(self._iter_data()):
            if self.subplots:
                ax = self.axes[i]
                style = 'k'
            else:
                style = ''  # empty string ignored
                ax = self.ax
            if self.style:
                style = self.style

            plotf(ax, x, y, style, label=label, **self.kwds)
            ax.grid(self.grid)