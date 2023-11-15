def top_segment_proportions_sparse_csr(data, indptr, ns):
    # work around https://github.com/numba/numba/issues/5056
    indptr = indptr.astype(np.int64)
    ns = np.sort(ns)
    maxidx = ns[-1]
    sums = np.zeros((indptr.size - 1), dtype=data.dtype)
    values = np.zeros((indptr.size - 1, len(ns)), dtype=np.float64)
    # Just to keep it simple, as a dense matrix
    partitioned = np.zeros((indptr.size - 1, maxidx), dtype=data.dtype)
    for i in numba.prange(indptr.size - 1):
        start, end = indptr[i], indptr[i + 1]
        sums[i] = np.sum(data[start:end])
        if end - start <= maxidx:
            partitioned[i, : end - start] = data[start:end]
        elif (end - start) > maxidx:
            partitioned[i, :] = -(np.partition(-data[start:end], maxidx))[:maxidx]
        partitioned[i, :] = np.partition(partitioned[i, :], maxidx - ns)
    partitioned = partitioned[:, ::-1][:, :ns[-1]]
    acc = np.zeros((indptr.size - 1), dtype=data.dtype)
    prev = 0
    # can’t use enumerate due to https://github.com/numba/numba/issues/2625
    for j in range(ns.size):
        acc += partitioned[:, prev:ns[j]].sum(axis=1)
        values[:, j] = acc
        prev = ns[j]
    return values / sums.reshape((indptr.size - 1, 1))