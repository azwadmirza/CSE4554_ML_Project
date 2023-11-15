    def _compute_map_reduce_metadata(self, axis, new_parts, preserve_index=True):
        """
        Computes metadata for the result of reduce function.

        Parameters
        ----------
        axis: int,
            The axis on which reduce function was applied
        new_parts: numpy 2D array
            Partitions with the result of applied function
        preserve_index: boolean
            The flag to preserve labels for the reduced axis.

        Returns
        -------
        BasePandasFrame
            Pandas series containing the reduced data.
        """
        new_axes, new_axes_lengths = [0, 0], [0, 0]

        new_axes[axis] = ["__reduced__"]
        new_axes[axis ^ 1] = (
            self.axes[axis ^ 1]
            if preserve_index
            else self._compute_axis_labels(axis ^ 1, new_parts)
        )

        new_axes_lengths[axis] = [1]
        new_axes_lengths[axis ^ 1] = (
            self._axes_lengths[axis ^ 1] if preserve_index else None
        )

        if (axis == 0 or self._dtypes is None) and preserve_index:
            new_dtypes = self._dtypes
        elif preserve_index:
            new_dtypes = pandas.Series(
                [find_common_type(self.dtypes.values)], index=new_axes[axis]
            )
        else:
            new_dtypes = None

        return self.__constructor__(
            new_parts,
            *new_axes,
            *new_axes_lengths,
            new_dtypes,
            validate_axes="reduced",
        )