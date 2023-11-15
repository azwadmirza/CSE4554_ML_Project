    def render_plot(self):
        for i, plot in enumerate(self.plots):
            plot.setData(y=pg.np.array(self.plot_data[1][i]), x=pg.np.array(self.plot_data[0]))