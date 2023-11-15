    def _validate_axis_equality(self, axis: int):
        """
        Validates internal and external indices of modin_frame at the specified axis.

        Parameters
        ----------
            axis : int,
                Axis to validate indices along
        """
        internal_axis = self._frame_mgr_cls.get_indices(
            axis, self._partitions, lambda df: df.axes[axis]
        )
        is_equals = self.axes[axis].equals(internal_axis)
        if not is_equals:
            self._set_axis(axis, self.axes[axis])