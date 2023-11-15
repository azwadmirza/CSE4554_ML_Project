    def _make_plot(self):
        # this is slightly deceptive
        if self.use_index and self._use_dynamic_x():
            data = self._maybe_convert_index(self.data)
            self._make_ts_plot(data, **self.kwds)
        else:
            lines = []
            labels = []
            x = self._get_xticks(convert_period=True)

            has_colors, colors = self._get_colors()
            def _maybe_add_color(kwargs, style, i):
                if (not has_colors and
                    (style is None or re.match('[a-z]+', style) is None)
                    and 'color' not in kwargs):
                    kwargs['color'] = colors[i % len(colors)]

            plotf = self._get_plot_function()

            for i, (label, y) in enumerate(self._iter_data()):
                ax = self._get_ax(i)
                style = self._get_style(i, label)
                kwds = self.kwds.copy()

                _maybe_add_color(kwds, style, i)

                label = _stringify(label)

                mask = com.isnull(y)
                if mask.any():
                    y = np.ma.array(y)
                    y = np.ma.masked_where(mask, y)

                kwds['label'] = label
                if style is None:
                    args = (ax, x, y)
                else:
                    args = (ax, x, y, style)

                newline = plotf(*args, **kwds)[0]
                lines.append(newline)
                leg_label = label
                if self.mark_right and self.on_right(i):
                    leg_label += ' (right)'
                labels.append(leg_label)
                ax.grid(self.grid)

            self._make_legend(lines, labels)