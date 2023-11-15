def _nanpercentile(a, q, axis=None, out=None, overwrite_input=False,
                   interpolation='linear', keepdims=False):
    """
    Private function that doesn't support extended axis or keepdims.
    These methods are extended to this function using _ureduce
    See nanpercentile for parameter usage

    """
    if axis is None:
        part = a.ravel()
        result = _nanpercentile1d(part, q, overwrite_input, interpolation)
    else:
        result = np.apply_along_axis(_nanpercentile1d, axis, a, q,
                                     overwrite_input, interpolation)
        # apply_along_axis fills in collapsed axis with results.
        # Move that axis to the beginning to match percentile's
        # convention.
        if q.ndim != 0:
            result = np.swapaxes(result, 0, axis)
    if out is not None:
        out[...] = result
    return result