    def _copartition(self, axis, other, how, sort, force_repartition=False):
        """
        Copartition two dataframes.

        Perform aligning of partitions, index and partition blocks.

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
        force_repartition : bool, default False
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

        # define helper functions
        def get_axis_lengths(partitions, axis):
            if axis:
                return [obj.width() for obj in partitions[0]]
            return [obj.length() for obj in partitions.T[0]]

        self_index = self.axes[axis]
        others_index = [o.axes[axis] for o in other]
        joined_index, make_reindexer = self._join_index_objects(
            axis, [self_index] + others_index, how, sort
        )

        # define conditions for reindexing and repartitioning `self` frame
        do_reindex_self = not self_index.equals(joined_index)
        do_repartition_self = force_repartition or do_reindex_self

        # perform repartitioning and reindexing for `self` frame if needed
        if do_repartition_self:
            reindexed_self = self._frame_mgr_cls.map_axis_partitions(
                axis,
                self._partitions,
                # self frame has 0 idx
                make_reindexer(do_reindex_self, 0),
            )
        else:
            reindexed_self = self._partitions

        # define length of `self` and `other` frames to aligning purpose
        self_lengths = get_axis_lengths(reindexed_self, axis)
        others_lengths = [o._axes_lengths[axis] for o in other]

        # define conditions for reindexing and repartitioning `other` frames
        do_reindex_others = [not index.equals(joined_index) for index in others_index]

        do_repartition_others = [None] * len(other)
        for i in range(len(other)):
            do_repartition_others[i] = (
                force_repartition
                or do_reindex_others[i]
                or others_lengths[i] != self_lengths
            )

        # perform repartitioning and reindexing for `other` frames if needed
        reindexed_other_list = [None] * len(other)
        for i in range(len(other)):
            if do_repartition_others[i]:
                reindexed_other_list[i] = other[i]._frame_mgr_cls.map_axis_partitions(
                    axis,
                    other[i]._partitions,
                    # indices of others frame start from 1 (0 - self frame)
                    make_reindexer(do_reindex_others[i], 1 + i),
                    lengths=self_lengths,
                )
            else:
                reindexed_other_list[i] = other[i]._partitions

        return reindexed_self, reindexed_other_list, joined_index