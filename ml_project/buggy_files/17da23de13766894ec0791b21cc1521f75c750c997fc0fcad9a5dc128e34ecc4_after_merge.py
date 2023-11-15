def unique(x, return_counts=False):
    """ Equivalent of np.unique that supports sparse or dense matrices. """
    if not sp.issparse(x):
        return np.unique(x, return_counts=return_counts)

    implicit_zeros = np.prod(x.shape) - x.nnz
    explicit_zeros = not np.all(x.data)
    r = np.unique(x.data, return_counts=return_counts)
    if not implicit_zeros:
        return r
    if return_counts:
        if explicit_zeros:
            r[1][r[0] == 0.] += implicit_zeros
            return r
        return np.insert(r[0], 0, 0), np.insert(r[1], 0, implicit_zeros)
    else:
        if explicit_zeros:
            return r
        return np.insert(r, 0, 0)