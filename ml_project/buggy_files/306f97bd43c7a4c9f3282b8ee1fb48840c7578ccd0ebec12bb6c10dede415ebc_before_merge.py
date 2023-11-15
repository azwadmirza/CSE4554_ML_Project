    def validate(self):
        super(Rolling, self).validate()

        # we allow rolling on a datetimelike index
        if (self.is_datetimelike and
                isinstance(self.window, (compat.string_types, DateOffset))):

            # must be monotonic for on
            if not self._on.is_monotonic:
                formatted = self.on or 'index'
                raise ValueError("{0} must be "
                                 "monotonic".format(formatted))

            from pandas.tseries.frequencies import to_offset
            try:
                freq = to_offset(self.window)
            except (TypeError, ValueError):
                raise ValueError("passed window {0} in not "
                                 "compat with a datetimelike "
                                 "index".format(self.window))

            # we don't allow center
            if self.center:
                raise NotImplementedError("center is not implemented "
                                          "for datetimelike and offset "
                                          "based windows")

            # this will raise ValueError on non-fixed freqs
            self.window = freq.nanos
            self.win_type = 'freq'

            # min_periods must be an integer
            if self.min_periods is None:
                self.min_periods = 1

        elif not is_integer(self.window):
            raise ValueError("window must be an integer")
        elif self.window < 0:
            raise ValueError("window must be non-negative")