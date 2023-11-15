    def _tile_both_dataframes(cls, op):
        # if both of the inputs are DataFrames, axis is just ignored
        left, right = op.inputs
        df = op.outputs[0]
        nsplits = [[], []]
        splits = _MinMaxSplitInfo()

        # first, we decide the chunk size on each axis
        # we perform the same logic for both index and columns
        for axis, index_type in enumerate(['index_value', 'columns']):
            if not cls._need_shuffle_on_axis(left, right, index_type, axis):
                left_chunk_index_min_max = cls._get_chunk_index_min_max(left, index_type, axis)
                right_chunk_index_min_max = cls._get_chunk_index_min_max(right, index_type, axis)
                # no need to do shuffle on this axis
                if len(left_chunk_index_min_max[0]) == 1 and len(right_chunk_index_min_max[0]) == 1:
                    # both left and right has only 1 chunk
                    left_splits, right_splits = \
                        [left_chunk_index_min_max[0]],  [right_chunk_index_min_max[0]]
                else:
                    left_splits, right_splits = split_monotonic_index_min_max(
                        *(left_chunk_index_min_max + right_chunk_index_min_max))
                left_increase = left_chunk_index_min_max[1]
                right_increase = right_chunk_index_min_max[1]
                splits[axis] = _AxisMinMaxSplitInfo(left_splits, left_increase,
                                                    right_splits, right_increase)
                nsplits[axis].extend(np.nan for _ in itertools.chain(*left_splits))
            else:
                # do shuffle
                left_chunk_size = left.chunk_shape[axis]
                right_chunk_size = right.chunk_shape[axis]
                out_chunk_size = max(left_chunk_size, right_chunk_size)
                nsplits[axis].extend(np.nan for _ in range(out_chunk_size))

        out_shape = tuple(len(ns) for ns in nsplits)
        if splits.all_axes_can_split():
            # no shuffle for all axes
            out_chunks = cls._gen_out_chunks_without_shuffle(op, splits, out_shape, left, right)
        elif splits.one_axis_can_split():
            # one axis needs shuffle
            out_chunks = cls._gen_out_chunks_with_one_shuffle(op, splits, out_shape, left, right)
        else:
            # all axes need shuffle
            assert splits.no_axis_can_split()
            out_chunks = cls._gen_out_chunks_with_all_shuffle(op, out_shape, left, right)

        new_op = op.copy()
        return new_op.new_dataframes(op.inputs, df.shape,
                                     nsplits=tuple(tuple(ns) for ns in nsplits),
                                     chunks=out_chunks, dtypes=df.dtypes,
                                     index_value=df.index_value, columns_value=df.columns)