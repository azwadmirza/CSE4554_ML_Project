def strided_windows(ndarray, window_size):
    """
    Produce a numpy.ndarray of windows, as from a sliding window.

    >>> strided_windows(np.arange(5), 2)
    array([[0, 1],
           [1, 2],
           [2, 3],
           [3, 4]])
    >>> strided_windows(np.arange(10), 5)
    array([[0, 1, 2, 3, 4],
           [1, 2, 3, 4, 5],
           [2, 3, 4, 5, 6],
           [3, 4, 5, 6, 7],
           [4, 5, 6, 7, 8],
           [5, 6, 7, 8, 9]])

    Args:
    ----
    ndarray: either a numpy.ndarray or something that can be converted into one.
    window_size: sliding window size.
    :param window_size:
    :return: numpy.ndarray of the subsequences produced by sliding a window of the given size over
             the `ndarray`. Since this uses striding, the individual arrays are views rather than
             copies of `ndarray`. Changes to one view modifies the others and the original.
    """
    ndarray = np.asarray(ndarray)
    if window_size == ndarray.shape[0]:
        return np.array([ndarray])
    elif window_size > ndarray.shape[0]:
        return np.ndarray((0, 0))

    stride = ndarray.strides[0]
    return np.lib.stride_tricks.as_strided(
        ndarray, shape=(ndarray.shape[0] - window_size + 1, window_size),
        strides=(stride, stride))