    def _make_ts_plot(self, data, **kwargs):
        from pandas.tseries.plotting import tsplot

        plotf = self._get_plot_function()

        if isinstance(data, Series):
            ax, _ = self._get_ax_and_style(0) #self.axes[0]

            label = com._stringify(self.label)
            tsplot(data, plotf, ax=ax, label=label, style=self.style,
                   **kwargs)
            ax.grid(self.grid)
        else:
            for i, col in enumerate(data.columns):
                ax, _ = self._get_ax_and_style(i)
                label = com._stringify(col)
                tsplot(data[col], plotf, ax=ax, label=label, **kwargs)
                ax.grid(self.grid)