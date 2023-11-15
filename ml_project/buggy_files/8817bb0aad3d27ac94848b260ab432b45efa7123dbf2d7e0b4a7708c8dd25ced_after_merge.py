    def groupby_reduce(
        self, axis, by, map_func, reduce_func, new_index=None, new_columns=None
    ):
        """Groupby another dataframe and aggregate the result.

        Args:
            axis: The axis to groupby and aggregate over.
            by: The dataframe to group by.
            map_func: The map component of the aggregation.
            reduce_func: The reduce component of the aggregation.
            new_index: (optional) The index of the result. We may know this in advance,
                and if not provided it must be computed.
            new_columns: (optional) The columns of the result. We may know this in
                advance, and if not provided it must be computed.

        Returns:
             A new dataframe.
        """
        new_partitions = self._frame_mgr_cls.groupby_reduce(
            axis, self._partitions, by._partitions, map_func, reduce_func
        )
        new_axes = [
            self._compute_axis_labels(i, new_partitions)
            if new_axis is None
            else new_axis
            for i, new_axis in enumerate([new_index, new_columns])
        ]

        return self.__constructor__(new_partitions, *new_axes)