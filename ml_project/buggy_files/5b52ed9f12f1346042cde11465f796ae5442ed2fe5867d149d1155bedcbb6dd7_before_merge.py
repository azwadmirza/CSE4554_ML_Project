    def apply_index(self, i):
        """
        Vectorized apply of DateOffset to DatetimeIndex,
        raises NotImplentedError for offsets without a
        vectorized implementation.

        Parameters
        ----------
        i : DatetimeIndex

        Returns
        -------
        y : DatetimeIndex
        """

        if type(self) is not DateOffset:
            raise NotImplementedError("DateOffset subclass {name} "
                                      "does not have a vectorized "
                                      "implementation".format(
                                          name=self.__class__.__name__))
        kwds = self.kwds
        relativedelta_fast = {'years', 'months', 'weeks', 'days', 'hours',
                              'minutes', 'seconds', 'microseconds'}
        # relativedelta/_offset path only valid for base DateOffset
        if (self._use_relativedelta and
                set(kwds).issubset(relativedelta_fast)):

            months = ((kwds.get('years', 0) * 12 +
                       kwds.get('months', 0)) * self.n)
            if months:
                shifted = liboffsets.shift_months(i.asi8, months)
                i = type(i)(shifted, freq=i.freq, dtype=i.dtype)

            weeks = (kwds.get('weeks', 0)) * self.n
            if weeks:
                # integer addition on PeriodIndex is deprecated,
                #   so we directly use _time_shift instead
                asper = i.to_period('W')
                if not isinstance(asper._data, np.ndarray):
                    # unwrap PeriodIndex --> PeriodArray
                    asper = asper._data
                shifted = asper._time_shift(weeks)
                i = shifted.to_timestamp() + i.to_perioddelta('W')

            timedelta_kwds = {k: v for k, v in kwds.items()
                              if k in ['days', 'hours', 'minutes',
                                       'seconds', 'microseconds']}
            if timedelta_kwds:
                delta = Timedelta(**timedelta_kwds)
                i = i + (self.n * delta)
            return i
        elif not self._use_relativedelta and hasattr(self, '_offset'):
            # timedelta
            return i + (self._offset * self.n)
        else:
            # relativedelta with other keywords
            kwd = set(kwds) - relativedelta_fast
            raise NotImplementedError("DateOffset with relativedelta "
                                      "keyword(s) {kwd} not able to be "
                                      "applied vectorized".format(kwd=kwd))