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
        if new_columns is None:
            new_columns = self._frame_mgr_cls.get_indices(
                1, new_partitions, lambda df: df.columns
            )
        if new_index is None:
            new_index = self._frame_mgr_cls.get_indices(
                0, new_partitions, lambda df: df.index
            )
        if axis == 0:
            new_widths = self._column_widths
            new_lengths = None
        else:
            new_widths = None
            new_lengths = self._row_lengths
        return self.__constructor__(
            new_partitions, new_index, new_columns, new_lengths, new_widths
        )