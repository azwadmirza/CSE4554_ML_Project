def decide_chunk_sizes(shape, chunk_size, itemsize):
    """
    Decide how a given tensor can be split into chunk.

    :param shape: tensor's shape
    :param chunk_size: if dict provided, it's dimension id to chunk size;
                       if provided, it's the chunk size for each dimension.
    :param itemsize: element size
    :return: the calculated chunk size for each dimension
    :rtype: tuple
    """

    from ...config import options

    chunk_size = dictify_chunk_size(shape, chunk_size)
    nleft = len(shape) - len(chunk_size)
    if nleft < 0:
        raise ValueError("chunks have more dimensions than input tensor")
    if nleft == 0:
        return normalize_chunk_sizes(shape, tuple(chunk_size[j] for j in range(len(shape))))

    max_chunk_size = options.tensor.chunk_store_limit

    # normalize the dimension which specified first
    dim_to_normalized = {i: normalize_chunk_sizes((shape[i],), (c,))[0]
                         for i, c in six.iteritems(chunk_size)}

    left = {j: [] for j in range(len(shape)) if j not in dim_to_normalized}
    left_unsplit = {j: shape[j] for j in left}
    while True:
        nbytes_occupied = np.prod([max(c) for c in six.itervalues(dim_to_normalized)]) * itemsize
        dim_size = np.maximum(int(np.power(max_chunk_size / nbytes_occupied, 1 / float(len(left)))), 1)
        for j, ns in six.iteritems(left.copy()):
            unsplit = left_unsplit[j]
            ns.append(np.minimum(unsplit, dim_size))
            left_unsplit[j] -= ns[-1]
            if left_unsplit[j] <= 0:
                dim_to_normalized[j] = tuple(ns)
                del left[j]

        if len(left) == 0:
            break

    return tuple(dim_to_normalized[i] for i in range(len(dim_to_normalized)))