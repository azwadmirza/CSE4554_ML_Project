    def _apply_full_axis(
        self, axis, func, new_index=None, new_columns=None, dtypes=None
    ):
        """Perform a function across an entire axis.

        Note: The data shape may change as a result of the function.

        Args:
            axis: The axis to apply over.
            func: The function to apply.
            new_index: (optional) The index of the result. We may know this in advance,
                and if not provided it must be computed.
            new_columns: (optional) The columns of the result. We may know this in
                advance, and if not provided it must be computed.
            dtypes: (optional) The data types of the result. This is an optimization
                because there are functions that always result in a particular data
                type, and allows us to avoid (re)computing it.

        Returns:
            A new dataframe.
        """
        new_partitions = self._frame_mgr_cls.map_axis_partitions(
            axis, self._partitions, func
        )
        # Index objects for new object creation. This is shorter than if..else
        if new_columns is None:
            new_columns = self._frame_mgr_cls.get_indices(
                1, new_partitions, lambda df: df.columns
            )
        if new_index is None:
            new_index = self._frame_mgr_cls.get_indices(
                1, new_partitions, lambda df: df.index
            )
        # Length objects for new object creation. This is shorter than if..else
        # This object determines the lengths and widths based on the given parameters
        # and builds a dictionary used in the constructor below. 0 gives the row lengths
        # and 1 gives the column widths. Since the dimension of `axis` given may have
        # changed, we current just recompute it.
        lengths_objs = {
            axis: None,
            axis ^ 1: [self._row_lengths, self._column_widths][axis ^ 1],
        }
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
            lengths_objs[0],
            lengths_objs[1],
            dtypes,
        )