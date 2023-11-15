    def _validate_axis_equality(self, axis: int, force: bool = False):
        """
        Validates internal and external indices of modin_frame at the specified axis.

        Parameters
        ----------
            axis : int,
                Axis to validate indices along
            force : bool,
                Whether to update external indices with internal if their lengths
                do not match or raise an exception in that case.
        """
        internal_axis = self._frame_mgr_cls.get_indices(
            axis, self._partitions, lambda df: df.axes[axis]
        )
        is_equals = self.axes[axis].equals(internal_axis)
        is_lenghts_matches = len(self.axes[axis]) == len(internal_axis)
        if not is_equals:
            if force:
                new_axis = self.axes[axis] if is_lenghts_matches else internal_axis
                self._set_axis(axis, new_axis, cache_only=not is_lenghts_matches)
            else:
                self._set_axis(
                    axis, self.axes[axis],
                )