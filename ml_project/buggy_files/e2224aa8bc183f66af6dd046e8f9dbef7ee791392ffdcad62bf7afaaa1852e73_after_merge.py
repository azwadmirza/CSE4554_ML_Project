    def _map_reduce(self, axis, map_func, reduce_func=None, preserve_index=True):
        """
        Apply function that will reduce the data to a Pandas Series.

        Parameters
        ----------
            axis : 0 or 1
                0 for columns and 1 for rows.
            map_func : callable
                Callable function to map the dataframe.
            reduce_func : callable
                Callable function to reduce the dataframe.
                If none, then apply map_func twice. Default is None.
            preserve_index : boolean
                The flag to preserve index for default behavior
                map and reduce operations. Default is True.

        Returns
        -------
        BasePandasFrame
            A new dataframe.
        """
        map_func = self._build_mapreduce_func(axis, map_func)
        if reduce_func is None:
            reduce_func = map_func
        else:
            reduce_func = self._build_mapreduce_func(axis, reduce_func)

        map_parts = self._frame_mgr_cls.map_partitions(self._partitions, map_func)
        reduce_parts = self._frame_mgr_cls.map_axis_partitions(
            axis, map_parts, reduce_func
        )
        if preserve_index:
            return self._compute_map_reduce_metadata(axis, reduce_parts)
        else:
            if axis == 0:
                new_index = ["__reduced__"]
                new_columns = self._frame_mgr_cls.get_indices(
                    1, reduce_parts, lambda df: df.columns
                )
            else:
                new_index = self._frame_mgr_cls.get_indices(
                    0, reduce_parts, lambda df: df.index
                )
                new_columns = ["__reduced__"]
            return self.__constructor__(
                reduce_parts, new_index, new_columns, validate_axes="reduced"
            )