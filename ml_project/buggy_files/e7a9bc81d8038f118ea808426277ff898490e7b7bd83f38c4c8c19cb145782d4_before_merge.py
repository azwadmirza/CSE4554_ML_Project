def circvar(samples, high=2*pi, low=0, axis=None):
    """
    Compute the circular variance for samples assumed to be in a range

    Parameters
    ----------
    samples : array_like
        Input array.
    low : float or int, optional
        Low boundary for circular variance range.  Default is 0.
    high : float or int, optional
        High boundary for circular variance range.  Default is ``2*pi``.
    axis : int, optional
        Axis along which variances are computed.  The default is to compute
        the variance of the flattened array.

    Returns
    -------
    circvar : float
        Circular variance.

    Notes
    -----
    This uses a definition of circular variance that in the limit of small
    angles returns a number close to the 'linear' variance.

    """
    ang = (samples - low)*2*pi / (high-low)
    res = np.mean(exp(1j*ang), axis=axis)
    R = abs(res)
    return ((high-low)/2.0/pi)**2 * 2 * log(1/R)