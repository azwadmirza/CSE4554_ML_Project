    def _get_time_period_bins(self, axis):
        if not isinstance(axis, DatetimeIndex):
            raise TypeError('axis must be a DatetimeIndex, but got '
                            'an instance of %r' % type(axis).__name__)

        if not len(axis):
            binner = labels = PeriodIndex(data=[], freq=self.freq)
            return binner, [], labels

        labels = binner = PeriodIndex(start=axis[0], end=axis[-1],
                                      freq=self.freq)

        end_stamps = (labels + 1).asfreq(self.freq, 's').to_timestamp()
        if axis.tzinfo:
            end_stamps = end_stamps.tz_localize(axis.tzinfo)
        bins = axis.searchsorted(end_stamps, side='left')

        return binner, bins, labels