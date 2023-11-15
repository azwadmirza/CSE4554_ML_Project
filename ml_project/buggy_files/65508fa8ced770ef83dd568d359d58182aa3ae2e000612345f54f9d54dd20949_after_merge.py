    def _make_plot(self):
        colors = self.kwds.get('color', 'brgyk')
        rects = []
        labels = []

        ax = self._get_ax(0) #self.axes[0]

        bar_f = self.bar_f

        pos_prior = neg_prior = np.zeros(len(self.data))

        K = self.nseries

        for i, (label, y) in enumerate(self._iter_data()):
            label = com._stringify(label)
            kwds = self.kwds.copy()
            kwds['color'] = colors[i % len(colors)]

            if self.subplots:
                ax = self._get_ax(i) #self.axes[i]
                rect = bar_f(ax, self.ax_pos, y, 0.5, start=pos_prior,
                             linewidth=1, **kwds)
                ax.set_title(label)
            elif self.stacked:
                mask = y > 0
                start = np.where(mask, pos_prior, neg_prior)

                rect = bar_f(ax, self.ax_pos, y, 0.5, start=start,
                             label=label, linewidth=1, **kwds)
                pos_prior = pos_prior + np.where(mask, y, 0)
                neg_prior = neg_prior + np.where(mask, 0, y)
            else:
                rect = bar_f(ax, self.ax_pos + i * 0.75 / K, y, 0.75 / K,
                             start=pos_prior, label=label, **kwds)
            rects.append(rect)
            labels.append(label)

        if self.legend and not self.subplots:
            patches =[r[0] for r in rects]
            self.axes[0].legend(patches, labels, loc='best',
                                title=self.legend_title)