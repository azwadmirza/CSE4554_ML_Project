    def apply_func_to_select_indices_along_full_axis(
        self, axis, func, indices, keep_remaining=False
    ):
        """Applies a function to a select subset of full columns/rows.

        Note: This should be used when you need to apply a function that relies
            on some global information for the entire column/row, but only need
            to apply a function to a subset.

        Important: For your func to operate directly on the indices provided,
            it must use `internal_indices` as a keyword argument.

        Args:
            axis: The axis to apply the function over (0 - rows, 1 - columns)
            func: The function to apply.
            indices: The global indices to apply the func to.
            keep_remaining: Whether or not to keep the other partitions.
                Some operations may want to drop the remaining partitions and
                keep only the results.

        Returns:
            A new BaseBlockPartitions object, the type of object that called this.
        """
        if self.partitions.size == 0:
            return np.array([[]])
        if isinstance(indices, dict):
            dict_indices = indices
            indices = list(indices.keys())
        else:
            dict_indices = None
        if not isinstance(indices, list):
            indices = [indices]
        partitions_dict = self._get_dict_of_block_index(axis, indices)
        preprocessed_func = self.preprocess_func(func)
        # Since we might be keeping the remaining blocks that are not modified,
        # we have to also keep the block_partitions object in the correct
        # direction (transpose for columns).
        if not axis:
            partitions_for_apply = self.column_partitions
            partitions_for_remaining = self.partitions.T
        else:
            partitions_for_apply = self.row_partitions
            partitions_for_remaining = self.partitions
        # We may have a command to perform different functions on different
        # columns at the same time. We attempt to handle this as efficiently as
        # possible here. Functions that use this in the dictionary format must
        # accept a keyword argument `func_dict`.
        if dict_indices is not None:
            if not keep_remaining:
                result = np.array(
                    [
                        partitions_for_apply[i].apply(
                            preprocessed_func,
                            func_dict={
                                idx: dict_indices[idx] for idx in partitions_dict[i]
                            },
                        )
                        for i in partitions_dict
                    ]
                )
            else:
                result = np.array(
                    [
                        partitions_for_remaining[i]
                        if i not in partitions_dict
                        else self._apply_func_to_list_of_partitions(
                            preprocessed_func,
                            partitions_for_apply[i],
                            func_dict={
                                idx: dict_indices[idx] for idx in partitions_dict[i]
                            },
                        )
                        for i in range(len(partitions_for_apply))
                    ]
                )
        else:
            if not keep_remaining:
                # See notes in `apply_func_to_select_indices`
                result = np.array(
                    [
                        partitions_for_apply[i].apply(
                            preprocessed_func, internal_indices=partitions_dict[i]
                        )
                        for i in partitions_dict
                    ]
                )
            else:
                # See notes in `apply_func_to_select_indices`
                result = np.array(
                    [
                        partitions_for_remaining[i]
                        if i not in partitions_dict
                        else partitions_for_apply[i].apply(
                            preprocessed_func, internal_indices=partitions_dict[i]
                        )
                        for i in range(len(partitions_for_remaining))
                    ]
                )
        return (
            self.__constructor__(result.T) if not axis else self.__constructor__(result)
        )