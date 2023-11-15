    def _make_plot(self):
        import matplotlib as mpl
        colors = self._get_colors()
        rects = []
        labels = []

        ax = self._get_ax(0)  # self.axes[0]

        bar_f = self.bar_f

        pos_prior = neg_prior = np.zeros(len(self.data))

        K = self.nseries

        for i, (label, y) in enumerate(self._iter_data()):
            label = com.pprint_thing(label)
            kwds = self.kwds.copy()
            kwds['color'] = colors[i % len(colors)]

            start =0
            if self.log:
                start = 1
                if any(y < 1):
                    # GH3254
                    start = 0 if mpl.__version__ == "1.2.1" else None

            if self.subplots:
                ax = self._get_ax(i)  # self.axes[i]

                rect = bar_f(ax, self.ax_pos, y,  self.bar_width,
                             start = start,
                             **kwds)
                ax.set_title(label)
            elif self.stacked:
                mask = y > 0
                start = np.where(mask, pos_prior, neg_prior)
                rect = bar_f(ax, self.ax_pos, y, self.bar_width, start=start,
                             label=label, **kwds)
                pos_prior = pos_prior + np.where(mask, y, 0)
                neg_prior = neg_prior + np.where(mask, 0, y)
            else:
                rect = bar_f(ax, self.ax_pos + i * 0.75 / K, y, 0.75 / K,
                             start = start,
                              label=label, **kwds)
            rects.append(rect)
            labels.append(label)

        if self.legend and not self.subplots:
            patches = [r[0] for r in rects]
            self.axes[0].legend(patches, labels, loc='best',
                                title=self.legend_title)