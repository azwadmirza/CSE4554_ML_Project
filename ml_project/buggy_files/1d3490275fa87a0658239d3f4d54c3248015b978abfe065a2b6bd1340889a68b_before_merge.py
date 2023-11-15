    def filter_full_axis(self, axis, func):
        """Filter data based on the function provided along an entire axis.

        Args:
            axis: The axis to filter over.
            func: The function to use for the filter. This function should filter the
                data itself.

        Returns:
            A new dataframe.
        """
        new_partitions = self._frame_mgr_cls.map_axis_partitions(
            axis, self._partitions, func, keep_partitioning=True
        )
        if axis == 0:
            new_index = self.index
            new_lengths = self._row_lengths
            new_widths = None  # We do not know what the resulting widths will be
            new_columns = self._frame_mgr_cls.get_indices(
                1, new_partitions, lambda df: df.columns
            )
        else:
            new_columns = self.columns
            new_lengths = None  # We do not know what the resulting lengths will be
            new_widths = self._column_widths
            new_index = self._frame_mgr_cls.get_indices(
                0, new_partitions, lambda df: df.index
            )
        return self.__constructor__(
            new_partitions,
            new_index,
            new_columns,
            new_lengths,
            new_widths,
            self.dtypes if axis == 0 else None,
        )