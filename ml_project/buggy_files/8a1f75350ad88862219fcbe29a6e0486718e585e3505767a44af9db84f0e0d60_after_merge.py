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

        axis_validate_mask = [validate_index, validate_columns]
        new_axes = [
            self._compute_axis_labels(axis, new_partitions)
            if should_validate
            else self.axes[axis]
            for axis, should_validate in enumerate(axis_validate_mask)
        ]

        new_lengths = [
            self._axes_lengths[axis]
            if len(new_axes[axis]) == len(self.axes[axis])
            else None
            for axis in [0, 1]
        ]

        return self.__constructor__(
            new_partitions,
            *new_axes,
            *new_lengths,
            dtypes=dtypes,
        )