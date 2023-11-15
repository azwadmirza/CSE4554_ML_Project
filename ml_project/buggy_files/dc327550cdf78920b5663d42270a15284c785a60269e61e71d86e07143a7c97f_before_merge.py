    def cummin(self, axis=None, skipna=True, *args, **kwargs):
        """Perform a cumulative minimum across the DataFrame.

        Args:
            axis (int): The axis to cummin on.
            skipna (bool): True to skip NA values, false otherwise.

        Returns:
            The cumulative minimum of the DataFrame.
        """
        axis = pandas.DataFrame()._get_axis_number(axis) if axis is not None else 0
        return DataFrame(
            data_manager=self._data_manager.cummin(axis=axis, skipna=skipna, **kwargs)
        )