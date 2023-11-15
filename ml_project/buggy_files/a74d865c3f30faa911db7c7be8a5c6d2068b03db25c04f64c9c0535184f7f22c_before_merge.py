    def _make_plot(self):
        from scipy.stats import gaussian_kde
        plotf = self._get_plot_function()
        for i, (label, y) in enumerate(self._iter_data()):

            ax, style = self._get_ax_and_style(i)

            if self.style:
                style = self.style
            gkde = gaussian_kde(y)
            sample_range = max(y) - min(y)
            ind = np.linspace(min(y) - 0.5 * sample_range,
                max(y) + 0.5 * sample_range, 1000)
            ax.set_ylabel("Density")
            plotf(ax, ind, gkde.evaluate(ind), style, label=label, **self.kwds)
            ax.grid(self.grid)