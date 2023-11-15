    def broadcast_apply_select_indices(
        self,
        axis,
        func,
        other,
        apply_indices=None,
        numeric_indices=None,
        keep_remaining=False,
        broadcast_all=True,
        new_index=None,
        new_columns=None,
    ):
        """
        Applyies `func` to select indices at specified axis and broadcasts
        partitions of `other` frame.

        Parameters
        ----------
            axis : int,
                Axis to apply function along
            func : callable,
                Function to apply
            other : BasePandasFrame,
                Partitions of which should be broadcasted
            apply_indices : list,
                List of labels to apply (if `numeric_indices` are not specified)
            numeric_indices : list,
                Numeric indices to apply (if `apply_indices` are not specified)
            keep_remaining : Whether or not to drop the data that is not computed over.
            broadcast_all : Whether broadcast the whole axis of right frame to every
                partition or just a subset of it.
            new_index : Index, (optional)
                The index of the result. We may know this in advance,
                and if not provided it must be computed
            new_columns : Index, (optional)
                The columns of the result. We may know this in advance,
                and if not provided it must be computed.

        Returns
        -------
            BasePandasFrame
        """
        assert (
            apply_indices is not None or numeric_indices is not None
        ), "Indices to apply must be specified!"

        if other is None:
            if apply_indices is None:
                apply_indices = self.axes[axis][numeric_indices]
            return self._apply_select_indices(
                axis=axis,
                func=func,
                apply_indices=apply_indices,
                keep_remaining=keep_remaining,
                new_index=new_index,
                new_columns=new_columns,
            )

        if numeric_indices is None:
            old_index = self.index if axis else self.columns
            numeric_indices = old_index.get_indexer_for(apply_indices)

        dict_indices = self._get_dict_of_block_index(axis ^ 1, numeric_indices)
        broadcasted_dict = other._prepare_frame_to_broadcast(
            axis, dict_indices, broadcast_all=broadcast_all
        )
        new_partitions = self._frame_mgr_cls.broadcast_apply_select_indices(
            axis,
            func,
            self._partitions,
            other._partitions,
            dict_indices,
            broadcasted_dict,
            keep_remaining,
        )
        if new_index is None:
            new_index = self._frame_mgr_cls.get_indices(
                0, new_partitions, lambda df: df.index
            )
        if new_columns is None:
            new_columns = self._frame_mgr_cls.get_indices(
                1, new_partitions, lambda df: df.columns
            )
        return self.__constructor__(new_partitions, new_index, new_columns)