    def _make_plot(self):
        # this is slightly deceptive
        if self.use_index and self.has_ts_index:
            data = self._maybe_convert_index(self.data)
            self._make_ts_plot(data)
        else:
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