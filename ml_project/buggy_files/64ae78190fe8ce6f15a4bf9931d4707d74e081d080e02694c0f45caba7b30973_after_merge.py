def align_dataframe_dataframe(left, right):
    left_index_chunks = [c.index_value for c in left.cix[:, 0]]
    left_columns_chunks = [c.columns_value for c in left.cix[0, :]]
    right_index_chunks = [c.index_value for c in right.cix[:, 0]]
    right_columns_chunks = [c.columns_value for c in right.cix[0, :]]

    index_splits, index_nsplits = _calc_axis_splits(left.index_value, right.index_value,
                                                    left_index_chunks, right_index_chunks)
    columns_splits, columns_nsplits = _calc_axis_splits(left.columns_value, right.columns_value,
                                                        left_columns_chunks, right_columns_chunks)

    nsplits = [index_nsplits, columns_nsplits]
    out_chunk_shape = tuple(len(ns) for ns in nsplits)
    splits = _MinMaxSplitInfo(index_splits, columns_splits)

    left_chunks = _gen_dataframe_chunks(splits, out_chunk_shape, 0, left)
    right_chunks = _gen_dataframe_chunks(splits, out_chunk_shape, 1, right)

    return nsplits, out_chunk_shape, left_chunks, right_chunks