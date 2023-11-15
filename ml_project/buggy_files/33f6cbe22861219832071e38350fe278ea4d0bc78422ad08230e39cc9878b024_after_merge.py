    def broadcast_apply(
        self, axis, func, other, join_type="left", preserve_labels=True, dtypes=None
    ):
        """
        Broadcast partitions of other dataframe partitions and apply a function.

        Parameters
        ----------
            axis: int,
                The axis to broadcast over.
            func: callable,
                The function to apply.
            other: BasePandasFrame
                The Modin DataFrame to broadcast.
            join_type: str (optional)
                The type of join to apply.
            preserve_labels: boolean (optional)
                Whether or not to keep labels from this Modin DataFrame.
            dtypes: "copy" or None (optional)
                 Whether to keep old dtypes or infer new dtypes from data.

        Returns
        -------
            BasePandasFrame
        """
        # Only sort the indices if they do not match
        left_parts, right_parts, joined_index = self._copartition(
            axis, other, join_type, sort=not self.axes[axis].equals(other.axes[axis])
        )
        # unwrap list returned by `copartition`.
        right_parts = right_parts[0]
        new_frame = self._frame_mgr_cls.broadcast_apply(
            axis, func, left_parts, right_parts
        )
        if dtypes == "copy":
            dtypes = self._dtypes
        new_index = self.index
        new_columns = self.columns
        if not preserve_labels:
            if axis == 1:
                new_columns = joined_index
            else:
                new_index = joined_index
        return self.__constructor__(
            new_frame, new_index, new_columns, None, None, dtypes=dtypes
        )