    def cumprod(self, axis=None, skipna=True, *args, **kwargs):
        """Perform a cumulative product across the DataFrame.

        Args:
            axis (int): The axis to take product on.
            skipna (bool): True to skip NA values, false otherwise.

        Returns:
            The cumulative product of the DataFrame.
        """
        axis = pandas.DataFrame()._get_axis_number(axis) if axis is not None else 0
        self._validate_dtypes(numeric_only=True)
        return DataFrame(
            data_manager=self._data_manager.cumprod(axis=axis, skipna=skipna, **kwargs)
        )