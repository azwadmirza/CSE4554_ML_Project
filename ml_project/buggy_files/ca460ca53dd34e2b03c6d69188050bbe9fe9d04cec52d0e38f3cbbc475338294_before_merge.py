    def _copartition(self, axis, other, how, sort, force_repartition=False):
        """
        Copartition two dataframes.

        Parameters
        ----------
            axis : 0 or 1
                The axis to copartition along (0 - rows, 1 - columns).
            other : BasePandasFrame
                The other dataframes(s) to copartition against.
            how : str
                How to manage joining the index object ("left", "right", etc.)
            sort : boolean
                Whether or not to sort the joined index.
            force_repartition : boolean
                Whether or not to force the repartitioning. By default,
                this method will skip repartitioning if it is possible. This is because
                reindexing is extremely inefficient. Because this method is used to
                `join` or `append`, it is vital that the internal indices match.

        Returns
        -------
        Tuple
            A tuple (left data, right data list, joined index).
        """
        if isinstance(other, type(self)):
            other = [other]
        if all(o.axes[axis].equals(self.axes[axis]) for o in other):
            return (
                self._partitions,
                [self._simple_shuffle(axis, o) for o in other],
                self.axes[axis].copy(),
            )
        index_other_obj = [o.axes[axis] for o in other]
        joined_index = self._join_index_objects(axis, index_other_obj, how, sort)
        # We have to set these because otherwise when we perform the functions it may
        # end up serializing this entire object.
        left_old_idx = self.axes[axis]
        right_old_idxes = index_other_obj

        # Start with this and we'll repartition the first time, and then not again.
        if not left_old_idx.equals(joined_index) or force_repartition:
            reindexed_self = self._frame_mgr_cls.map_axis_partitions(
                axis, self._partitions, lambda df: df.reindex(joined_index, axis=axis)
            )
        else:
            reindexed_self = self._partitions
        reindexed_other_list = []

        for i in range(len(other)):
            if right_old_idxes[i].equals(joined_index) and not force_repartition:
                reindexed_other = other[i]._partitions
            else:
                reindexed_other = other[i]._frame_mgr_cls.map_axis_partitions(
                    axis,
                    other[i]._partitions,
                    lambda df: df.reindex(joined_index, axis=axis),
                )
            reindexed_other_list.append(reindexed_other)
        return reindexed_self, reindexed_other_list, joined_index