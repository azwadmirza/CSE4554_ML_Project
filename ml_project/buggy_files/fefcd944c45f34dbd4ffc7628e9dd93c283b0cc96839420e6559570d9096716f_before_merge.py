def _need_align_map(input_chunk, index_min_max, column_min_max,
                    dummy_index_splits=False, dummy_column_splits=False):
    if not dummy_index_splits:
        assert not index_min_max[0] is None and not index_min_max[2] is None
    if isinstance(input_chunk, SERIES_CHUNK_TYPE):
        if input_chunk.index_value is None:
            return True
        if input_chunk.index_value.min_max != index_min_max:
            return True
    else:
        if not dummy_index_splits:
            if input_chunk.index_value is None or input_chunk.index_value.min_max != index_min_max:
                return True
        if not dummy_column_splits:
            if input_chunk.columns_value is None or input_chunk.columns_value.min_max != column_min_max:
                return True
    return False