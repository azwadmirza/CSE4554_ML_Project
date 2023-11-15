    def _post_plot_logic(self):
        df = self.data

        if self.subplots and self.legend:
            self.axes[0].legend(loc='best')

        condition = (df.index.is_all_dates
                     and not self.subplots
                     or (self.subplots and self.sharex))

        for ax in self.axes:
            if condition:
                format_date_labels(ax)