    def _post_plot_logic(self):
        df = self.data

        if self.legend:
            if self.subplots:
                for ax in self.axes:
                    ax.legend(loc='best')
            else:
                self.axes[0].legend(loc='best')

        condition = (not self._use_dynamic_x
                     and df.index.is_all_dates
                     and not self.subplots
                     or (self.subplots and self.sharex))

        index_name = self._get_index_name()

        for ax in self.axes:
            if condition:
                format_date_labels(ax)

            if index_name is not None:
                ax.set_xlabel(index_name)