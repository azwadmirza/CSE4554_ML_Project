    def to_period(self, freq=None, copy=True) -> "Series":
        """
        Convert Series from DatetimeIndex to PeriodIndex with desired
        frequency (inferred from index if not passed).

        Parameters
        ----------
        freq : str, default None
            Frequency associated with the PeriodIndex.
        copy : bool, default True
            Whether or not to return a copy.

        Returns
        -------
        Series
            Series with index converted to PeriodIndex.
        """
        new_values = self._values
        if copy:
            new_values = new_values.copy()

        if not isinstance(self.index, DatetimeIndex):
            raise TypeError(f"unsupported Type {type(self.index).__name__}")
        new_index = self.index.to_period(freq=freq)  # type: ignore
        return self._constructor(new_values, index=new_index).__finalize__(
            self, method="to_period"
        )