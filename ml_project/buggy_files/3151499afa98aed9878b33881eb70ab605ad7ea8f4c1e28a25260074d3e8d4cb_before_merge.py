    def to_timestamp(self, freq=None, how='S'):
        """
        Return the Timestamp at the start/end of the period

        Parameters
        ----------
        freq : string or DateOffset, default frequency of PeriodIndex
            Target frequency
        how: str, default 'S' (start)
            'S', 'E'. Can be aliased as case insensitive
            'Start', 'Finish', 'Begin', 'End'

        Returns
        -------
        Timestamp
        """
        if freq is None:
            base, mult = _gfc(self.freq)
            new_val = self
        else:
            base, mult = _gfc(freq)
            new_val = self.asfreq(freq, how)

        dt64 = plib.period_ordinal_to_dt64(new_val.ordinal, base)
        ts_freq = _period_rule_to_timestamp_rule(new_val.freq, how=how)
        return Timestamp(dt64, offset=to_offset(ts_freq))