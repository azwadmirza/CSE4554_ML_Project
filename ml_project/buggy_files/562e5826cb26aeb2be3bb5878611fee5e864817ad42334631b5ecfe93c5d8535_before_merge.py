    def _adorn_subplots(self):
        if self.subplots:
            to_adorn = self.axes
        else:
            to_adorn = [self.ax]

        # todo: sharex, sharey handling?

        for ax in to_adorn:
            if self.yticks is not None:
                ax.set_yticks(self.yticks)

            if self.xticks is not None:
                ax.set_xticks(self.xticks)

            if self.ylim is not None:
                ax.set_ylim(self.ylim)

            if self.xlim is not None:
                ax.set_xlim(self.xlim)

            ax.grid(self.grid)

        if self.legend and not self.subplots:
            self.ax.legend(loc='best')

        if self.title:
            if self.subplots:
                self.fig.suptitle(self.title)
            else:
                self.ax.set_title(self.title)

        if self._need_to_set_index:
            xticklabels = [_stringify(key) for key in self.data.index]
            for ax_ in self.axes:
                # ax_.set_xticks(self.xticks)
                ax_.set_xticklabels(xticklabels, rotation=self.rot)