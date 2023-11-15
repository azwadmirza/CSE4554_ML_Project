def _calc_axis_splits(left_axis, right_axis, left_axis_chunks, right_axis_chunks):
    if _axis_need_shuffle(left_axis, right_axis, left_axis_chunks, right_axis_chunks):
        # do shuffle
        out_chunk_size = max(len(left_axis_chunks), len(right_axis_chunks))
        return None, [np.nan for _ in range(out_chunk_size)]
    else:
        # no need to do shuffle on this axis
        left_chunk_index_min_max, left_increase = _get_chunk_index_min_max(left_axis, left_axis_chunks)
        right_chunk_index_min_max, right_increase = _get_chunk_index_min_max(right_axis, right_axis_chunks)
        if len(left_chunk_index_min_max) == 1 and len(right_chunk_index_min_max) == 1:
            # both left and right has only 1 chunk
            left_splits, right_splits = [left_chunk_index_min_max], [right_chunk_index_min_max]
        else:
            left_splits, right_splits = split_monotonic_index_min_max(
                left_chunk_index_min_max, left_increase, right_chunk_index_min_max, right_increase)
        splits = _AxisMinMaxSplitInfo(left_splits, left_increase,
                                      right_splits, right_increase)
        nsplits = [np.nan for _ in itertools.chain(*left_splits)]
        return splits, nsplits