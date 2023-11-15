    def _make_plot(self):
        # this is slightly deceptive
        if self.use_index and self._use_dynamic_x():
            data = self._maybe_convert_index(self.data)
            self._make_ts_plot(data)
        else:
            x = self._get_xticks(convert_period=True)

            plotf = self._get_plot_function()

            for i, (label, y) in enumerate(self._iter_data()):

                ax, style = self._get_ax_and_style(i)

                if self.style:
                    style = self.style

                mask = com.isnull(y)
                if mask.any():
                    y = np.ma.array(y)
                    y = np.ma.masked_where(mask, y)

                plotf(ax, x, y, style, label=label, **self.kwds)
                ax.grid(self.grid)