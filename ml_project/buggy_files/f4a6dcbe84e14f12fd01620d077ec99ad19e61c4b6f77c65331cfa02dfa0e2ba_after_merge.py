    def _get_new_index(self):
        """ return our new index """
        ax = self.ax

        if len(ax) == 0:
            values = []
        else:
            start = ax[0].asfreq(self.freq, how=self.convention)
            end = ax[-1].asfreq(self.freq, how='end')
            values = period_range(start, end, freq=self.freq).values

        return ax._shallow_copy(values, freq=self.freq)