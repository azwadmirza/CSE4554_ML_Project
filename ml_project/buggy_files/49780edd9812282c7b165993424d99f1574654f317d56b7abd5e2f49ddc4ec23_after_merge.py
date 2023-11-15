    def broadcast_apply_full_axis(
        self,
        axis,
        func,
        other,
        new_index=None,
        new_columns=None,
        dtypes=None,
    ):
        """Broadcast partitions of other dataframe partitions and apply a function along full axis.

        Parameters
        ----------
            axis : 0 or 1
                The axis to apply over (0 - rows, 1 - columns).
            func : callable
                The function to apply.
            other : other Modin frame to broadcast
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
             A new Modin DataFrame
        """
        new_partitions = self._frame_mgr_cls.broadcast_axis_partitions(
            axis=axis,
            left=self._partitions,
            right=other if other is None else other._partitions,
            apply_func=self._build_mapreduce_func(axis, func),
            keep_partitioning=True,
        )
        # Index objects for new object creation. This is shorter than if..else
        new_axes = [
            self._compute_axis_labels(i, new_partitions)
            if new_axis is None
            else new_axis
            for i, new_axis in enumerate([new_index, new_columns])
        ]
        if dtypes == "copy":
            dtypes = self._dtypes
        elif dtypes is not None:
            dtypes = pandas.Series(
                [np.dtype(dtypes)] * len(new_axes[1]), index=new_axes[1]
            )
        return self.__constructor__(
            new_partitions,
            *new_axes,
            None,
            None,
            dtypes,
            validate_axes="all" if new_partitions.size != 0 else False,
        )