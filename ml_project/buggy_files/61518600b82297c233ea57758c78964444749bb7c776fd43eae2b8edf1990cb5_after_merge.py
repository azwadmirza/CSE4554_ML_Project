    def _ensure_localized(self, result, ambiguous='raise'):
        """
        ensure that we are re-localized

        This is for compat as we can then call this on all datetimelike
        indexes generally (ignored for Period/Timedelta)

        Parameters
        ----------
        result : DatetimeIndex / i8 ndarray
        ambiguous : str, bool, or bool-ndarray
            default 'raise'

        Returns
        -------
        localized DTI
        """

        # reconvert to local tz
        if getattr(self, 'tz', None) is not None:
            if not isinstance(result, ABCIndexClass):
                result = self._simple_new(result)
            result = result.tz_localize(self.tz, ambiguous=ambiguous)
        return result