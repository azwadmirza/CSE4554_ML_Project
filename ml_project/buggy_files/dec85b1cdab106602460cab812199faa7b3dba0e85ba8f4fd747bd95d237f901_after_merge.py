    def _adjust_cbar(self, cbar, label, dim):
        noalpha = math.floor(self.style[self.cyclic_index].get('alpha', 1)) == 1
        if (cbar.solids and noalpha):
            cbar.solids.set_edgecolor("face")
        cbar.set_label(label)
        if isinstance(self.cbar_ticks, ticker.Locator):
            cbar.ax.yaxis.set_major_locator(self.cbar_ticks)
        elif self.cbar_ticks == 0:
            cbar.set_ticks([])
        elif isinstance(self.cbar_ticks, int):
            locator = ticker.MaxNLocator(self.cbar_ticks)
            cbar.ax.yaxis.set_major_locator(locator)
        elif isinstance(self.cbar_ticks, list):
            if all(isinstance(t, tuple) for t in self.cbar_ticks):
                ticks, labels = zip(*self.cbar_ticks)
            else:
                ticks, labels = zip(*[(t, dim.pprint_value(t))
                                        for t in self.cbar_ticks])
            cbar.set_ticks(ticks)
            cbar.set_ticklabels(labels)