    def render_plot(self):
        for i, plot in enumerate(self.plots):
            plot.setData(x=pg.np.array(list(self.plot_data.keys())),
                         y=pg.np.array([data[i] for data in self.plot_data.values()]))