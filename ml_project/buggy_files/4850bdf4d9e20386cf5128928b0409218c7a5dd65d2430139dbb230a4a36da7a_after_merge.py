def _slice_target(target, dims, both_slices, slice_nav=None, issignal=False):
    """Slices the target if appropriate

    Parameters
    ----------
    target : object
        Target object
    dims : tuple
        (navigation_dimensions, signal_dimensions) of the original object that
        is sliced
    both_slices : tuple
        (original_slices, array_slices) of the operation that is performed
    slice_nav : {bool, None}
        if None, target is returned as-is. Otherwise navigation and signal
        dimensions are sliced for True and False values respectively.
    issignal : bool
        if the target is signal and should be sliced as one
    """
    if slice_nav is None:
        return target
    if target is None:
        return None
    nav_dims, sig_dims = dims
    slices, array_slices = both_slices
    if slice_nav is True:  # check explicitly for safety
        if issignal:
            return target.inav[slices]
        sl = tuple(array_slices[:nav_dims])
        if isinstance(target, np.ndarray):
            return np.atleast_1d(target[sl])
        if isinstance(target, dArray):
            return target[sl]
        raise ValueError(
            'tried to slice with navigation dimensions, but was neither a '
            'signal nor an array')
    if slice_nav is False:  # check explicitly
        if issignal:
            return target.isig[slices]
        sl = tuple(array_slices[-sig_dims:])
        if isinstance(target, np.ndarray):
            return np.atleast_1d(target[sl])
        if isinstance(target, dArray):
            return target[sl]
        raise ValueError(
            'tried to slice with navigation dimensions, but was neither a '
            'signal nor an array')