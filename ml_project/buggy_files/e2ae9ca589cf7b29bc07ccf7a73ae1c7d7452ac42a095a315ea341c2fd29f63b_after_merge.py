def plan_rechunks(tileable, new_chunk_size, itemsize, threshold=None, chunk_size_limit=None):
    threshold = threshold or options.rechunk.threshold
    chunk_size_limit = chunk_size_limit or options.rechunk.chunk_size_limit

    if len(new_chunk_size) != tileable.ndim:
        raise ValueError('Provided chunks should have %d dimensions, got %d' % (
            tileable.ndim, len(new_chunk_size)))

    steps = []

    if itemsize > 0:
        chunk_size_limit /= itemsize
    chunk_size_limit = max([int(chunk_size_limit),
                            _largest_chunk_size(tileable.nsplits),
                            _largest_chunk_size(new_chunk_size)])

    graph_size_threshold = threshold * (_chunk_number(tileable.nsplits) + _chunk_number(new_chunk_size))

    chunk_size = curr_chunk_size = tileable.nsplits
    first_run = True
    while True:
        graph_size = _estimate_graph_size(chunk_size, new_chunk_size)
        if graph_size < graph_size_threshold:
            break
        if not first_run:
            chunk_size = _find_split_rechunk(curr_chunk_size, new_chunk_size, graph_size * threshold)
        chunks_size, memory_limit_hit = _find_merge_rechunk(chunk_size, new_chunk_size, chunk_size_limit)
        if chunk_size == curr_chunk_size or chunk_size == new_chunk_size:
            break
        steps.append(chunk_size)
        curr_chunk_size = chunk_size
        if not memory_limit_hit:
            break
        first_run = False

    return steps + [new_chunk_size]