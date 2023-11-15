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
            how = _validate_end_alias(how)
            if how == 'S':
                base = _freq_mod.get_to_timestamp_base(base)
                freq = _freq_mod._get_freq_str(base)
                new_val = self.asfreq(freq, how)
            else:
                new_val = self
        else:
            base, mult = _gfc(freq)
            new_val = self.asfreq(freq, how)

        dt64 = plib.period_ordinal_to_dt64(new_val.ordinal, base)
        return Timestamp(dt64)