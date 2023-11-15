    def to_timestamp(self, freq=None, how="start", copy=True) -> "Series":
        """
        Cast to DatetimeIndex of Timestamps, at *beginning* of period.

        Parameters
        ----------
        freq : str, default frequency of PeriodIndex
            Desired frequency.
        how : {'s', 'e', 'start', 'end'}
            Convention for converting period to timestamp; start of period
            vs. end.
        copy : bool, default True
            Whether or not to return a copy.

        Returns
        -------
        Series with DatetimeIndex
        """
        new_values = self._values
        if copy:
            new_values = new_values.copy()

        if not isinstance(self.index, PeriodIndex):
            raise TypeError(f"unsupported Type {type(self.index).__name__}")
        new_index = self.index.to_timestamp(freq=freq, how=how)  # type: ignore
        return self._constructor(new_values, index=new_index).__finalize__(
            self, method="to_timestamp"
        )