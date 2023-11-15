    def searchsorted(self, value, side='left', sorter=None):
        if isinstance(value, Period):
            if value.freq != self.freq:
                msg = DIFFERENT_FREQ_INDEX.format(self.freqstr, value.freqstr)
                raise IncompatibleFrequency(msg)
            value = value.ordinal
        elif isinstance(value, compat.string_types):
            try:
                value = Period(value, freq=self.freq).ordinal
            except DateParseError:
                raise KeyError("Cannot interpret '{}' as period".format(value))

        return self._ndarray_values.searchsorted(value, side=side,
                                                 sorter=sorter)