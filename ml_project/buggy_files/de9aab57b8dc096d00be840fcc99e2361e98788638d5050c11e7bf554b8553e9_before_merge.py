def align_dataframe_series(left, right, axis='columns'):
    if axis == 'columns' or axis == 1:
        left_columns_chunks = [c.columns for c in left.cix[0, :]]
        right_index_chunks = [c.index_value for c in right.chunks]
        index_splits, index_nsplits = _calc_axis_splits(left.columns, right.index_value,
                                                        left_columns_chunks, right_index_chunks)
        dummy_splits, dummy_nsplits = _build_dummy_axis_split(left.chunk_shape[0]), left.nsplits[0]
        nsplits = [dummy_nsplits, index_nsplits]
        out_chunk_shape = tuple(len(ns) for ns in nsplits)
        left_chunks = _gen_dataframe_chunks(_MinMaxSplitInfo(dummy_splits, index_splits), out_chunk_shape, 0, left)
        right_chunks = _gen_series_chunks(_MinMaxSplitInfo(index_splits, None), (out_chunk_shape[1],), 1, right)
    else:
        assert axis == 'index' or axis == 0
        left_index_chunks = [c.index_value for c in left.cix[:, 0]]
        right_index_chunks = [c.index_value for c in right.chunks]
        index_splits, index_nsplits = _calc_axis_splits(left.index_value, right.index_value,
                                                        left_index_chunks, right_index_chunks)
        dummy_splits, dummy_nsplits = _build_dummy_axis_split(left.chunk_shape[1]), left.nsplits[1]
        nsplits = [index_nsplits, dummy_nsplits]
        out_chunk_shape = tuple(len(ns) for ns in nsplits)
        left_chunks = _gen_dataframe_chunks(_MinMaxSplitInfo(index_splits, dummy_splits), out_chunk_shape, 0, left)
        right_chunks = _gen_series_chunks(_MinMaxSplitInfo(index_splits, None), (out_chunk_shape[0],), 1, right)

    return nsplits, out_chunk_shape, left_chunks, right_chunks