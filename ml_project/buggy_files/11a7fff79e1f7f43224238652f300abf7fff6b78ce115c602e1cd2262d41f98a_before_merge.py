    def _set_axis(self, axis, new_axis):
        """Replaces the current labels at the specified axis with the new one

        Parameters
        ----------
            axis : int,
                Axis to set labels along
            new_axis : Index,
                The replacement labels
        """
        if axis:
            self._set_columns(new_axis)
        else:
            self._set_index(new_axis)