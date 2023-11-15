def normalize_chunk_sizes(shape, chunk_size):
    shape = normalize_shape(shape)
    if not isinstance(chunk_size, tuple):
        if isinstance(chunk_size, Iterable):
            chunk_size = tuple(chunk_size)
        elif isinstance(chunk_size, int):
            chunk_size = (chunk_size,) * len(shape)

    if len(shape) != len(chunk_size):
        raise ValueError('Chunks must have the same dimemsion, '
                         f'got shape: {shape}, chunks: {chunk_size}')

    chunk_sizes = []
    for size, chunk in zip(shape, chunk_size):
        if isinstance(chunk, Iterable):
            if not isinstance(chunk, tuple):
                chunk = tuple(chunk)

            if sum(chunk) != size:
                raise ValueError('chunks shape should be of the same length, '
                                 f'got shape: {size}, chunks: {chunk}')
            chunk_sizes.append(chunk)
        else:
            assert isinstance(chunk, int)

            if size == 0:
                sizes = (0,)
            else:
                sizes = tuple(chunk for _ in range(int(size / chunk))) + \
                    (tuple() if size % chunk == 0 else (size % chunk,))
            chunk_sizes.append(sizes)

    return tuple(chunk_sizes)