    def _make_ts_plot(self, data, **kwargs):
        from pandas.tseries.plotting import tsplot
        import matplotlib.pyplot as plt
        kwargs = kwargs.copy()
        cycle = ''.join(plt.rcParams.get('axes.color_cycle', list('bgrcmyk')))
        colors = kwargs.pop('colors', ''.join(cycle))

        plotf = self._get_plot_function()
        lines = []
        labels = []

        def to_leg_label(label, i):
            if self.mark_right and self.on_right(i):
                return label + ' (right)'
            return label

        if isinstance(data, Series):
            ax = self._get_ax(0) #self.axes[0]
            style = self.style or ''
            label = com._stringify(self.label)
            if re.match('[a-z]+', style) is None:
                kwargs['color'] = colors[0]

            newlines = tsplot(data, plotf, ax=ax, label=label, style=self.style,
                             **kwargs)
            ax.grid(self.grid)
            lines.append(newlines[0])
            leg_label = to_leg_label(label, 0)
            labels.append(leg_label)
        else:
            for i, col in enumerate(data.columns):
                label = com._stringify(col)
                ax = self._get_ax(i)
                style = self._get_style(i, col)
                kwds = kwargs.copy()
                if re.match('[a-z]+', style) is None:
                    kwds['color'] = colors[i % len(colors)]

                newlines = tsplot(data[col], plotf, ax=ax, label=label,
                                  style=style, **kwds)

                lines.append(newlines[0])
                leg_label = to_leg_label(label, i)
                labels.append(leg_label)
                ax.grid(self.grid)

        self._make_legend(lines, labels)