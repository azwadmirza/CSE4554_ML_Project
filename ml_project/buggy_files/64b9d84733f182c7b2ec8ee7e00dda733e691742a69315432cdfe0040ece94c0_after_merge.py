    def _ensure_localized(self, arg, ambiguous='raise', from_utc=False):
        """
        ensure that we are re-localized

        This is for compat as we can then call this on all datetimelike
        indexes generally (ignored for Period/Timedelta)

        Parameters
        ----------
        arg : DatetimeIndex / i8 ndarray
        ambiguous : str, bool, or bool-ndarray, default 'raise'
        from_utc : bool, default False
            If True, localize the i8 ndarray to UTC first before converting to
            the appropriate tz. If False, localize directly to the tz.

        Returns
        -------
        localized DTI
        """

        # reconvert to local tz
        if getattr(self, 'tz', None) is not None:
            if not isinstance(arg, ABCIndexClass):
                arg = self._simple_new(arg)
            if from_utc:
                arg = arg.tz_localize('UTC').tz_convert(self.tz)
            else:
                arg = arg.tz_localize(self.tz, ambiguous=ambiguous)
        return arg