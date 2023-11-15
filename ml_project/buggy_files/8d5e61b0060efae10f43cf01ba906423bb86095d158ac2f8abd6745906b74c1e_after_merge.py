    def _adorn_subplots(self):
        to_adorn = self.axes

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

        if self.title:
            if self.subplots:
                self.fig.suptitle(self.title)
            else:
                self.axes[0].set_title(self.title)

        if self._need_to_set_index:
            labels = [_stringify(key) for key in self.data.index]
            labels = dict(zip(range(len(self.data.index)), labels))

            for ax_ in self.axes:
                # ax_.set_xticks(self.xticks)
                xticklabels = [labels.get(x, '') for x in ax_.get_xticks()]
                ax_.set_xticklabels(xticklabels, rotation=self.rot)