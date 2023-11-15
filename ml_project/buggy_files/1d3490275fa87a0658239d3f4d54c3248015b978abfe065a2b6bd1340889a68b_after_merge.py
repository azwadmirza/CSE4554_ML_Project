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
        new_axes, new_lengths = [0, 0], [0, 0]

        new_axes[axis] = self.axes[axis]
        new_axes[axis ^ 1] = self._compute_axis_labels(axis ^ 1, new_partitions)

        new_lengths[axis] = self._axes_lengths[axis]
        new_lengths[axis ^ 1] = None  # We do not know what the resulting widths will be

        return self.__constructor__(
            new_partitions,
            *new_axes,
            *new_lengths,
            self.dtypes if axis == 0 else None,
        )