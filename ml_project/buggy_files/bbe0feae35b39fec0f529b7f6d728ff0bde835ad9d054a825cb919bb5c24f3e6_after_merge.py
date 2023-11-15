    def _apply_index_days(self, i, roll):
        """Add days portion of offset to DatetimeIndex i

        Parameters
        ----------
        i : DatetimeIndex
        roll : ndarray[int64_t]

        Returns
        -------
        result : DatetimeIndex
        """
        nanos = (roll % 2) * Timedelta(days=self.day_of_month - 1).value
        return i + nanos.astype('timedelta64[ns]')