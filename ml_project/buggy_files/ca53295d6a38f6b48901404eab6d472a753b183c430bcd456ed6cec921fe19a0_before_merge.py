    def apply_func_to_select_indices(self, axis, func, indices, keep_remaining=False):
        """Applies a function to select indices.

        Note: Your internal function must take a kwarg `internal_indices` for
            this to work correctly. This prevents information leakage of the
            internal index to the external representation.

        Args:
            axis: The axis to apply the func over.
            func: The function to apply to these indices.
            indices: The indices to apply the function to.
            keep_remaining: Whether or not to keep the other partitions.
                Some operations may want to drop the remaining partitions and
                keep only the results.

        Returns:
            A new BaseBlockPartitions object, the type of object that called this.
        """
        # Handling dictionaries has to be done differently, but we still want
        # to figure out the partitions that need to be applied to, so we will
        # store the dictionary in a separate variable and assign `indices` to
        # the keys to handle it the same as we normally would.
        if isinstance(indices, dict):
            dict_indices = indices
            indices = list(indices.keys())
        else:
            dict_indices = None
        if not isinstance(indices, list):
            indices = [indices]
        partitions_dict = self._get_dict_of_block_index(
            axis, indices, ordered=not keep_remaining
        )
        if not axis:
            partitions_for_apply = self.partitions.T
        else:
            partitions_for_apply = self.partitions
        # We may have a command to perform different functions on different
        # columns at the same time. We attempt to handle this as efficiently as
        # possible here. Functions that use this in the dictionary format must
        # accept a keyword argument `func_dict`.
        if dict_indices is not None:

            def local_to_global_idx(partition_id, local_idx):
                if partition_id == 0:
                    return local_idx
                if axis == 0:
                    cumulative_axis = np.cumsum(self.block_widths)
                else:
                    cumulative_axis = np.cumsum(self.block_lengths)
                return cumulative_axis[partition_id - 1] + local_idx

            if not keep_remaining:
                result = np.array(
                    [
                        self._apply_func_to_list_of_partitions(
                            func,
                            partitions_for_apply[o_idx],
                            func_dict={
                                i_idx: dict_indices[local_to_global_idx(o_idx, i_idx)]
                                for i_idx in list_to_apply
                                if i_idx >= 0
                            },
                        )
                        for o_idx, list_to_apply in partitions_dict
                    ]
                )
            else:
                result = np.array(
                    [
                        partitions_for_apply[i]
                        if i not in partitions_dict
                        else self._apply_func_to_list_of_partitions(
                            func,
                            partitions_for_apply[i],
                            func_dict={
                                idx: dict_indices[local_to_global_idx(i, idx)]
                                for idx in partitions_dict[i]
                                if idx >= 0
                            },
                        )
                        for i in range(len(partitions_for_apply))
                    ]
                )
        else:
            if not keep_remaining:
                # We are passing internal indices in here. In order for func to
                # actually be able to use this information, it must be able to take in
                # the internal indices. This might mean an iloc in the case of Pandas
                # or some other way to index into the internal representation.
                result = np.array(
                    [
                        self._apply_func_to_list_of_partitions(
                            func,
                            partitions_for_apply[idx],
                            internal_indices=list_to_apply,
                        )
                        for idx, list_to_apply in partitions_dict
                    ]
                )
            else:
                # The difference here is that we modify a subset and return the
                # remaining (non-updated) blocks in their original position.
                result = np.array(
                    [
                        partitions_for_apply[i]
                        if i not in partitions_dict
                        else self._apply_func_to_list_of_partitions(
                            func,
                            partitions_for_apply[i],
                            internal_indices=partitions_dict[i],
                        )
                        for i in range(len(partitions_for_apply))
                    ]
                )
        return (
            self.__constructor__(result.T) if not axis else self.__constructor__(result)
        )