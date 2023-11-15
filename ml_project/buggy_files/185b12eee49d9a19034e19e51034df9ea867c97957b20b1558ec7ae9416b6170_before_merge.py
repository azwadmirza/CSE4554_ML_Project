def _median(a, axis=None, out=None, overwrite_input=False):
    if overwrite_input:
        if axis is None:
            asorted = a.ravel()
            asorted.sort()
        else:
            a.sort(axis=axis)
            asorted = a
    else:
        asorted = sort(a, axis=axis)
    if axis is None:
        axis = 0
    elif axis < 0:
        axis += a.ndim

    if asorted.ndim == 1:
        idx, odd = divmod(count(asorted), 2)
        return asorted[idx - (not odd) : idx + 1].mean()

    counts = asorted.shape[axis] - (asorted.mask).sum(axis=axis)
    h = counts // 2
    # create indexing mesh grid for all but reduced axis
    axes_grid = [np.arange(x) for i, x in enumerate(asorted.shape)
                 if i != axis]
    ind = np.meshgrid(*axes_grid, sparse=True, indexing='ij')
    # insert indices of low and high median
    ind.insert(axis, h - 1)
    low = asorted[tuple(ind)]
    low._sharedmask = False
    ind[axis] = h
    high = asorted[tuple(ind)]
    # duplicate high if odd number of elements so mean does nothing
    odd = counts % 2 == 1
    if asorted.ndim == 1:
        if odd:
            low = high
    else:
        low[odd] = high[odd]

    if np.issubdtype(asorted.dtype, np.inexact):
        # avoid inf / x = masked
        s = np.ma.sum([low, high], axis=0, out=out)
        np.true_divide(s.data, 2., casting='unsafe', out=s.data)
    else:
        s = np.ma.mean([low, high], axis=0, out=out)
    return s