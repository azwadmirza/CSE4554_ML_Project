    def _downsample(self, how, **kwargs):
        """
        Downsample the cython defined function

        Parameters
        ----------
        how : string / cython mapped function
        **kwargs : kw args passed to how function
        """

        # we may need to actually resample as if we are timestamps
        if self.kind == 'timestamp':
            return super(PeriodIndexResampler, self)._downsample(how, **kwargs)

        how = self._is_cython_func(how) or how
        ax = self.ax

        new_index = self._get_new_index()
        if len(new_index) == 0:
            return self._wrap_result(self._selected_obj.reindex(new_index))

        # Start vs. end of period
        memb = ax.asfreq(self.freq, how=self.convention)

        if is_subperiod(ax.freq, self.freq):
            # Downsampling
            rng = np.arange(memb.values[0], memb.values[-1] + 1)
            bins = memb.searchsorted(rng, side='right')
            grouper = BinGrouper(bins, new_index)
            return self._groupby_and_aggregate(grouper, how)
        elif is_superperiod(ax.freq, self.freq):
            return self.asfreq()
        elif ax.freq == self.freq:
            return self.asfreq()

        raise ValueError('Frequency {axfreq} cannot be '
                         'resampled to {freq}'.format(
                             axfreq=ax.freq,
                             freq=self.freq))