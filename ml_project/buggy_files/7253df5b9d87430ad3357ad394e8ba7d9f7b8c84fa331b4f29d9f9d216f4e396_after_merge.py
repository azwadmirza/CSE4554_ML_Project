    def _post_plot_logic(self):
        df = self.data

        if self.subplots and self.legend:
            for ax in self.axes:
                ax.legend(loc='best')