    def _map(self, func, dtypes=None, validate_index=False, validate_columns=False):
        """Perform a function that maps across the entire dataset.

        Pamareters
        ----------
            func : callable
                The function to apply.
            dtypes :
                (optional) The data types for the result. This is an optimization
                because there are functions that always result in a particular data
                type, and allows us to avoid (re)computing it.
            validate_index : bool, (default False)
                Is index validation required after performing `func` on partitions.
        Returns
        -------
            A new dataframe.
        """
        new_partitions = self._frame_mgr_cls.lazy_map_partitions(self._partitions, func)
        if dtypes == "copy":
            dtypes = self._dtypes
        elif dtypes is not None:
            dtypes = pandas.Series(
                [np.dtype(dtypes)] * len(self.columns), index=self.columns
            )
        if validate_index:
            new_index = self._frame_mgr_cls.get_indices(
                0, new_partitions, lambda df: df.index
            )
        else:
            new_index = self.index
        if len(new_index) != len(self.index):
            new_row_lengths = None
        else:
            new_row_lengths = self._row_lengths

        if validate_columns:
            new_columns = self._frame_mgr_cls.get_indices(
                1, new_partitions, lambda df: df.columns
            )
        else:
            new_columns = self.columns
        if len(new_columns) != len(self.columns):
            new_column_widths = None
        else:
            new_column_widths = self._column_widths
        return self.__constructor__(
            new_partitions,
            new_index,
            new_columns,
            new_row_lengths,
            new_column_widths,
            dtypes=dtypes,
        )