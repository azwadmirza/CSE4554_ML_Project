    def _post_plot_logic(self):
        df = self.data

        if self.legend:
            if self.subplots:
                for ax in self.axes:
                    ax.legend(loc='best')
            else:
                self.axes[0].legend(loc='best')

        condition = (not self.has_ts_index
                     and df.index.is_all_dates
                     and not self.subplots
                     or (self.subplots and self.sharex))

        for ax in self.axes:
            if condition:
                format_date_labels(ax)