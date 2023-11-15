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

        frames = [self] + other
        non_empty_frames_idx = [
            i for i, o in enumerate(frames) if o._partitions.size != 0
        ]

        # If all frames are empty
        if len(non_empty_frames_idx) == 0:
            return self._partitions, [o._partitions for o in other], joined_index

        base_frame_idx = non_empty_frames_idx[0]
        base_frame = frames[base_frame_idx]

        other_frames = frames[base_frame_idx + 1 :]

        # Picking first non-empty frame
        base_frame = frames[non_empty_frames_idx[0]]
        base_index = base_frame.axes[axis]

        # define conditions for reindexing and repartitioning `self` frame
        do_reindex_base = not base_index.equals(joined_index)
        do_repartition_base = force_repartition or do_reindex_base

        # perform repartitioning and reindexing for `base_frame` if needed
        if do_repartition_base:
            reindexed_base = base_frame._frame_mgr_cls.map_axis_partitions(
                axis,
                base_frame._partitions,
                make_reindexer(do_reindex_base, base_frame_idx),
            )
        else:
            reindexed_base = base_frame._partitions

        # define length of base and `other` frames to aligning purpose
        base_lengths = get_axis_lengths(reindexed_base, axis)
        others_lengths = [o._axes_lengths[axis] for o in other_frames]

        # define conditions for reindexing and repartitioning `other` frames
        do_reindex_others = [
            not o.axes[axis].equals(joined_index) for o in other_frames
        ]

        do_repartition_others = [None] * len(other_frames)
        for i in range(len(other_frames)):
            do_repartition_others[i] = (
                force_repartition
                or do_reindex_others[i]
                or others_lengths[i] != base_lengths
            )

        # perform repartitioning and reindexing for `other_frames` if needed
        reindexed_other_list = [None] * len(other_frames)
        for i in range(len(other_frames)):
            if do_repartition_others[i]:
                # indices of others frame start from `base_frame_idx` + 1
                reindexed_other_list[i] = other_frames[
                    i
                ]._frame_mgr_cls.map_axis_partitions(
                    axis,
                    other_frames[i]._partitions,
                    make_reindexer(do_repartition_others[i], base_frame_idx + 1 + i),
                    lengths=base_lengths,
                )
            else:
                reindexed_other_list[i] = other_frames[i]._partitions
        reindexed_frames = (
            [frames[i]._partitions for i in range(base_frame_idx)]
            + [reindexed_base]
            + reindexed_other_list
        )
        return reindexed_frames[0], reindexed_frames[1:], joined_index