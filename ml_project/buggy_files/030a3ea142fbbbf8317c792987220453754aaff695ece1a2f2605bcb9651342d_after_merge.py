def decide_series_chunk_size(shape, chunk_size, memory_usage):
    from ..config import options

    chunk_size = dictify_chunk_size(shape, chunk_size)
    average_memory_usage = memory_usage / shape[0] if shape[0] != 0 else memory_usage

    if len(chunk_size) == len(shape):
        return normalize_chunk_sizes(shape, chunk_size[0])

    max_chunk_size = options.chunk_store_limit
    series_chunk_size = max_chunk_size / average_memory_usage
    return normalize_chunk_sizes(shape, int(series_chunk_size))