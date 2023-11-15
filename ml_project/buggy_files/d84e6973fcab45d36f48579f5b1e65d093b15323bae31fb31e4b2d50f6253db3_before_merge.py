def mode(a, axis=0, nan_policy='propagate'):
    """
    Return an array of the modal (most common) value in the passed array.

    If there is more than one such value, only the smallest is returned.
    The bin-count for the modal bins is also returned.

    Parameters
    ----------
    a : array_like
        n-dimensional array of which to find mode(s).
    axis : int or None, optional
        Axis along which to operate. Default is 0. If None, compute over
        the whole array `a`.
    nan_policy : {'propagate', 'raise', 'omit'}, optional
        Defines how to handle when input contains nan. 'propagate' returns nan,
        'raise' throws an error, 'omit' performs the calculations ignoring nan
        values. Default is 'propagate'.

    Returns
    -------
    mode : ndarray
        Array of modal values.
    count : ndarray
        Array of counts for each mode.

    Examples
    --------
    >>> a = np.array([[6, 8, 3, 0],
    ...               [3, 2, 1, 7],
    ...               [8, 1, 8, 4],
    ...               [5, 3, 0, 5],
    ...               [4, 7, 5, 9]])
    >>> from scipy import stats
    >>> stats.mode(a)
    (array([[3, 1, 0, 0]]), array([[1, 1, 1, 1]]))

    To get mode of whole array, specify ``axis=None``:

    >>> stats.mode(a, axis=None)
    (array([3]), array([3]))

    """
    a, axis = _chk_asarray(a, axis)
    if a.size == 0:
        return ModeResult(np.array([]), np.array([]))

    contains_nan, nan_policy = _contains_nan(a, nan_policy)

    if contains_nan and nan_policy == 'omit':
        a = ma.masked_invalid(a)
        return mstats_basic.mode(a, axis)

    if (NumpyVersion(np.__version__) < '1.9.0') or (a.dtype == object and np.nan in set(a)):
        # Fall back to a slower method since np.unique does not work with NaN
        # or for older numpy which does not support return_counts
        scores = set(np.ravel(a))  # get ALL unique values
        testshape = list(a.shape)
        testshape[axis] = 1
        oldmostfreq = np.zeros(testshape, dtype=a.dtype)
        oldcounts = np.zeros(testshape, dtype=int)

        for score in scores:
            template = (a == score)
            counts = np.expand_dims(np.sum(template, axis), axis)
            mostfrequent = np.where(counts > oldcounts, score, oldmostfreq)
            oldcounts = np.maximum(counts, oldcounts)
            oldmostfreq = mostfrequent

        return ModeResult(mostfrequent, oldcounts)

    def _mode1D(a):
        vals, cnts = np.unique(a, return_counts=True)
        return vals[cnts.argmax()], cnts.max()

    # np.apply_along_axis will convert the _mode1D tuples to a numpy array, casting types in the process
    # This recreates the results without that issue
    # View of a, rotated so the requested axis is last
    in_dims = list(range(a.ndim))
    a_view = np.transpose(a, in_dims[:axis] + in_dims[axis+1:] + [axis])

    inds = np.ndindex(a_view.shape[:-1])
    modes = np.empty(a_view.shape[:-1], dtype=a.dtype)
    counts = np.zeros(a_view.shape[:-1], dtype=np.int)
    for ind in inds:
        modes[ind], counts[ind] = _mode1D(a_view[ind])
    newshape = list(a.shape)
    newshape[axis] = 1
    return ModeResult(modes.reshape(newshape), counts.reshape(newshape))