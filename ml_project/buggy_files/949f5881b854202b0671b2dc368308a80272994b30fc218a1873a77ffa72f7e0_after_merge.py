def _calc_axis_splits(left_axis, right_axis, left_axis_chunks, right_axis_chunks):
    if _axis_need_shuffle(left_axis, right_axis, left_axis_chunks, right_axis_chunks):
        # do shuffle
        out_chunk_size = max(len(left_axis_chunks), len(right_axis_chunks))
        return None, [np.nan for _ in range(out_chunk_size)]
    else:
        # no need to do shuffle on this axis
        if _is_index_identical(left_axis_chunks, right_axis_chunks):
            left_chunk_index_min_max = _get_chunk_index_min_max(left_axis_chunks)
            right_splits = left_splits = [[c] for c in left_chunk_index_min_max]
            right_increase = left_increase = None
        elif len(left_axis_chunks) == 1 and len(right_axis_chunks) == 1:
            left_splits = [_get_chunk_index_min_max(left_axis_chunks)]
            left_increase = left_axis_chunks[0].is_monotonic_decreasing
            right_splits = [_get_chunk_index_min_max(right_axis_chunks)]
            right_increase = right_axis_chunks[0].is_monotonic_decreasing
        else:
            left_chunk_index_min_max, left_increase = _get_monotonic_chunk_index_min_max(left_axis,
                                                                                         left_axis_chunks)
            right_chunk_index_min_max, right_increase = _get_monotonic_chunk_index_min_max(right_axis,
                                                                                           right_axis_chunks)
            left_splits, right_splits = split_monotonic_index_min_max(
                left_chunk_index_min_max, left_increase, right_chunk_index_min_max, right_increase)
        splits = _AxisMinMaxSplitInfo(left_splits, left_increase, right_splits, right_increase)
        nsplits = [np.nan for _ in itertools.chain(*left_splits)]
        return splits, nsplits