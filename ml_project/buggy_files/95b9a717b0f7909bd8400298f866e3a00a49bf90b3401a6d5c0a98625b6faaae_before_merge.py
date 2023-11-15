    def _adorn_subplots(self):
        """Common post process unrelated to data"""
        if len(self.axes) > 0:
            all_axes = self._get_axes()
            nrows, ncols = self._get_axes_layout()
            _handle_shared_axes(axarr=all_axes, nplots=len(all_axes),
                                naxes=nrows * ncols, nrows=nrows,
                                ncols=ncols, sharex=self.sharex,
                                sharey=self.sharey)

        for ax in self.axes:
            if self.yticks is not None:
                ax.set_yticks(self.yticks)

            if self.xticks is not None:
                ax.set_xticks(self.xticks)

            if self.ylim is not None:
                ax.set_ylim(self.ylim)

            if self.xlim is not None:
                ax.set_xlim(self.xlim)

            ax.grid(self.grid)

        if self.title:
            if self.subplots:
                self.fig.suptitle(self.title)
            else:
                self.axes[0].set_title(self.title)