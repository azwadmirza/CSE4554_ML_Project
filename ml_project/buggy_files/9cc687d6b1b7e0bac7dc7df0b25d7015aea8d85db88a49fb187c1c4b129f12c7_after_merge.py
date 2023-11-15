    def _make_plot(self):
        colors = 'brgyk'
        rects = []
        labels = []

        ax = self.axes[0]

        bar_f = self.bar_f

        pos_prior = neg_prior = np.zeros(len(self.data))

        K = self.nseries

        for i, (label, y) in enumerate(self._iter_data()):

            kwds = self.kwds.copy()
            if 'color' not in kwds:
                kwds['color'] = colors[i % len(colors)]

            if self.subplots:
                ax = self.axes[i]
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

            # Legend to the right of the plot
            # ax.legend(patches, labels, bbox_to_anchor=(1.05, 1),
            #           loc=2, borderaxespad=0.)
            # self.fig.subplots_adjust(right=0.80)

            ax.legend(patches, labels, loc='best',
                      title=self.legend_title)

        self.fig.subplots_adjust(top=0.8, wspace=0, hspace=0)