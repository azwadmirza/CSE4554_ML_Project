    def broadcast_apply(self, axis, func, other, preserve_labels=True, dtypes=None):
        """Broadcast partitions of other dataframe partitions and apply a function.

        Args:
            axis: The axis to broadcast over.
            func: The function to apply.
            other: The Modin DataFrame to broadcast.
            preserve_labels: Whether or not to keep labels from this Modin DataFrame.
            dtypes: "copy" or None. Whether to keep old dtypes or infer new dtypes from
                data.

        Returns:
             A new Modin DataFrame
        """
        assert preserve_labels, "`preserve_labels=False` Not Yet Implemented"
        # Only sort the indices if they do not match
        left_parts, right_parts, joined_index = self._copartition(
            axis, other, "left", sort=not self.axes[axis].equals(other.axes[axis])
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
        return self.__constructor__(
            new_frame, new_index, new_columns, None, None, dtypes=dtypes
        )