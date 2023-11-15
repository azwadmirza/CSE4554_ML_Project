    def _post_plot_logic(self):
        df = self.data

        if self.subplots and self.legend:
            self.axes[0].legend(loc='best')