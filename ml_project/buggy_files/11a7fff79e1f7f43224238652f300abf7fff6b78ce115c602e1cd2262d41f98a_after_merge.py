    def _set_axis(self, axis, new_axis, cache_only=False):
        """Replaces the current labels at the specified axis with the new one

        Parameters
        ----------
            axis : int,
                Axis to set labels along
            new_axis : Index,
                The replacement labels
            cache_only : bool,
                Whether to change only external indices, or propagate it
                into partitions
        """
        if axis:
            if not cache_only:
                self._set_columns(new_axis)
            else:
                self._columns_cache = ensure_index(new_axis)
        else:
            if not cache_only:
                self._set_index(new_axis)
            else:
                self._index_cache = ensure_index(new_axis)