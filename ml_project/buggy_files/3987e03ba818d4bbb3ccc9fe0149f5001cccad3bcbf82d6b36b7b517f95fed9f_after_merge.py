    def _fold_reduce(self, axis, func, preserve_index=True):
        """
        Apply function that reduce Manager to series but require knowledge of full axis.

        Parameters
        ----------
            axis : 0 or 1
                The axis to apply the function to (0 - index, 1 - columns).
            func : callable
                The function to reduce the Manager by. This function takes in a Manager.
            preserve_index : boolean
                The flag to preserve labels for the reduced axis.

        Returns
        -------
        BasePandasFrame
            Pandas series containing the reduced data.
        """
        func = self._build_mapreduce_func(axis, func)
        new_parts = self._frame_mgr_cls.map_axis_partitions(
            axis, self._partitions, func
        )
        return self._compute_map_reduce_metadata(
            axis, new_parts, preserve_index=preserve_index
        )