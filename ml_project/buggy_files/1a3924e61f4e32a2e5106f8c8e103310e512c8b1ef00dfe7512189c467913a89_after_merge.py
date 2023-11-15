    def _apply_full_axis(
        self, axis, func, new_index=None, new_columns=None, dtypes=None,
    ):
        """
        Perform a function across an entire axis.

        Parameters
        ----------
            axis : 0 or 1
                The axis to apply over (0 - rows, 1 - columns).
            func : callable
                The function to apply.
            new_index : list-like (optional)
                The index of the result. We may know this in advance,
                and if not provided it must be computed.
            new_columns : list-like (optional)
                The columns of the result. We may know this in
                advance, and if not provided it must be computed.
            dtypes : list-like (optional)
                The data types of the result. This is an optimization
                because there are functions that always result in a particular data
                type, and allows us to avoid (re)computing it.

        Returns
        -------
        BasePandasFrame
            A new dataframe.

        Notes
        -----
        The data shape may change as a result of the function.
        """
        new_partitions = self._frame_mgr_cls.map_axis_partitions(
            axis,
            self._partitions,
            self._build_mapreduce_func(axis, func),
            keep_partitioning=True,
        )
        # Index objects for new object creation. This is shorter than if..else
        if new_columns is None:
            new_columns = self._frame_mgr_cls.get_indices(
                1, new_partitions, lambda df: df.columns
            )
        if new_index is None:
            new_index = self._frame_mgr_cls.get_indices(
                0, new_partitions, lambda df: df.index
            )
        if dtypes == "copy":
            dtypes = self._dtypes
        elif dtypes is not None:
            dtypes = pandas.Series(
                [np.dtype(dtypes)] * len(new_columns), index=new_columns
            )
        return self.__constructor__(
            new_partitions,
            new_index,
            new_columns,
            None,
            None,
            dtypes,
            validate_axes="reduced",
        )