    def _binary_op(self, op, right_frame, join_type="outer"):
        """
        Perform an operation that requires joining with another dataframe.

        Parameters
        ----------
            op : callable
                The function to apply after the join.
            right_frame : BasePandasFrame
                The dataframe to join with.
            join_type : str (optional)
                The type of join to apply.

        Returns
        -------
        BasePandasFrame
            A new dataframe.
        """
        left_parts, right_parts, joined_index = self._copartition(
            0, right_frame, join_type, sort=True
        )
        # unwrap list returned by `copartition`.
        right_parts = right_parts[0]
        new_frame = self._frame_mgr_cls.binary_operation(
            1, left_parts, lambda l, r: op(l, r), right_parts
        )
        new_columns = self.columns.join(right_frame.columns, how=join_type)
        return self.__constructor__(new_frame, self.index, new_columns, None, None)