    def _validate_axis_equality(self, axis: int, force: bool = False):
        """
        Validates internal and external indices of modin_frame at the specified axis.

        Parameters
        ----------
            axis : 0 or 1
                Axis to validate indices along (0 - index, 1 - columns).
            force : boolean, default False
                Whether to update external indices with internal if their lengths
                do not match or raise an exception in that case.
        """
        internal_axis = self._compute_axis_labels(axis)
        self_axis = self.axes[axis]
        is_equals = self_axis.equals(internal_axis)
        if (
            isinstance(self_axis, DatetimeIndex)
            and isinstance(internal_axis, DatetimeIndex)
            and is_equals
        ):
            if getattr(self_axis, "freq") != getattr(internal_axis, "freq"):
                is_equals = False
                force = True
        is_lenghts_matches = len(self_axis) == len(internal_axis)
        if not is_equals:
            if not is_lenghts_matches:
                if axis:
                    self._column_widths_cache = None
                else:
                    self._row_lengths_cache = None
            new_axis = self_axis if is_lenghts_matches and not force else internal_axis
            self._set_axis(axis, new_axis, cache_only=not is_lenghts_matches)