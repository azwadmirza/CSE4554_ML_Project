def circmean(samples, high=2*pi, low=0, axis=None):
    """
    Compute the circular mean for samples in a range.

    Parameters
    ----------
    samples : array_like
        Input array.
    high : float or int, optional
        High boundary for circular mean range.  Default is ``2*pi``.
    low : float or int, optional
        Low boundary for circular mean range.  Default is 0.
    axis : int, optional
        Axis along which means are computed.  The default is to compute
        the mean of the flattened array.

    Returns
    -------
    circmean : float
        Circular mean.

    """
    samples, ang = _circfuncs_common(samples, high, low)
    res = angle(np.mean(exp(1j*ang), axis=axis))
    mask = res < 0
    if (mask.ndim > 0):
        res[mask] += 2*pi
    elif mask:
        res = res + 2*pi

    return res*(high-low)/2.0/pi + low