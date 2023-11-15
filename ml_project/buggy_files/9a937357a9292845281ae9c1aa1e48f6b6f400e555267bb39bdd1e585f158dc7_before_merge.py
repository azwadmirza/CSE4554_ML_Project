def _get_chunk_index_min_max(index, index_chunks):
    chunk_index_min_max = []
    for chunk in index_chunks:
        min_val = chunk.min_val
        min_val_close = chunk.min_val_close
        max_val = chunk.max_val
        max_val_close = chunk.max_val_close
        if min_val is None or max_val is None:
            return
        chunk_index_min_max.append((min_val, min_val_close, max_val, max_val_close))
    if index.is_monotonic_decreasing:
        return list(reversed(chunk_index_min_max)), False
    if _check_overlap(chunk_index_min_max):
        return
    return chunk_index_min_max, True