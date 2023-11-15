    def crop(self, tmin=None, tmax=None, include_tmax=True, verbose=None):
        """Crop a time interval from the epochs.

        Parameters
        ----------
        tmin : float | None
            Start time of selection in seconds.
        tmax : float | None
            End time of selection in seconds.
        %(include_tmax)s
        %(verbose_meth)s

        Returns
        -------
        epochs : instance of Epochs
            The cropped epochs object, modified in-place.

        Notes
        -----
        %(notes_tmax_included_by_default)s
        """
        # XXX this could be made to work on non-preloaded data...
        _check_preload(self, 'Modifying data of epochs')

        if tmin is None:
            tmin = self.tmin
        elif tmin < self.tmin:
            warn('tmin is not in epochs time interval. tmin is set to '
                 'epochs.tmin')
            tmin = self.tmin

        if tmax is None:
            tmax = self.tmax
        elif tmax > self.tmax:
            warn('tmax is not in epochs time interval. tmax is set to '
                 'epochs.tmax')
            tmax = self.tmax

        tmask = _time_mask(self.times, tmin, tmax, sfreq=self.info['sfreq'],
                           include_tmax=include_tmax)
        self._set_times(self.times[tmask])
        self._raw_times = self._raw_times[tmask]
        self._data = self._data[:, :, tmask]
        return self