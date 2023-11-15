    def _onselect(self, eclick, erelease, baseline, mode, layout):
        """Callback function called by rubber band selector in channel tfr."""
        import matplotlib.pyplot as plt
        from ..viz import plot_tfr_topomap
        if abs(eclick.x - erelease.x) < .1 or abs(eclick.y - erelease.y) < .1:
            return
        plt.ion()  # turn interactive mode on
        tmin = round(min(eclick.xdata, erelease.xdata) / 1000., 5)  # ms to s
        tmax = round(max(eclick.xdata, erelease.xdata) / 1000., 5)
        fmin = round(min(eclick.ydata, erelease.ydata), 5)  # Hz
        fmax = round(max(eclick.ydata, erelease.ydata), 5)
        tmin = min(self.times, key=lambda x: abs(x - tmin))  # find closest
        tmax = min(self.times, key=lambda x: abs(x - tmax))
        fmin = min(self.freqs, key=lambda x: abs(x - fmin))
        fmax = min(self.freqs, key=lambda x: abs(x - fmax))
        if tmin == tmax or fmin == fmax:
            logger.info('The selected area is too small. '
                        'Select a larger time-frequency window.')
            return

        types = list()
        if 'eeg' in self:
            types.append('eeg')
        if 'mag' in self:
            types.append('mag')
        if 'grad' in self:
            types.append('grad')
        fig = figure_nobar()
        fig.suptitle('{:.2f} s - {:.2f} s, {:.2f} Hz - {:.2f} Hz'.format(tmin,
                                                                         tmax,
                                                                         fmin,
                                                                         fmax),
                     y=0.04)
        for idx, ch_type in enumerate(types):
            ax = plt.subplot(1, len(types), idx + 1)
            plot_tfr_topomap(self, ch_type=ch_type, tmin=tmin, tmax=tmax,
                             fmin=fmin, fmax=fmax, layout=layout,
                             baseline=baseline, mode=mode, cmap=None,
                             title=ch_type, vmin=None, vmax=None,
                             axes=ax)