    def _setup_subplots(self):
        if self.subplots:
            nrows, ncols = self._get_layout()
            if self.ax is None:
                fig, axes = _subplots(nrows=nrows, ncols=ncols,
                                      sharex=self.sharex, sharey=self.sharey,
                                      figsize=self.figsize,
                                      secondary_y=self.secondary_y,
                                      data=self.data)
            else:
                fig, axes = _subplots(nrows=nrows, ncols=ncols,
                                      sharex=self.sharex, sharey=self.sharey,
                                      figsize=self.figsize, ax=self.ax,
                                      secondary_y=self.secondary_y,
                                      data=self.data)
        else:
            if self.ax is None:
                fig = self.plt.figure(figsize=self.figsize)
                ax = fig.add_subplot(111)
                ax = self._maybe_right_yaxis(ax)
            else:
                fig = self.ax.get_figure()
                ax = self._maybe_right_yaxis(self.ax)

            axes = [ax]

        self.fig = fig
        self.axes = axes