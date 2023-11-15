def circstd(samples, high=2*pi, low=0, axis=None):
    """
    Compute the circular standard deviation for samples assumed to be in the
    range [low to high].

    Parameters
    ----------
    samples : array_like
        Input array.
    low : float or int, optional
        Low boundary for circular standard deviation range.  Default is 0.
    high : float or int, optional
        High boundary for circular standard deviation range.
        Default is ``2*pi``.
    axis : int, optional
        Axis along which standard deviations are computed.  The default is
        to compute the standard deviation of the flattened array.

    Returns
    -------
    circstd : float
        Circular standard deviation.

    Notes
    -----
    This uses a definition of circular standard deviation that in the limit of
    small angles returns a number close to the 'linear' standard deviation.

    """
    ang = (samples - low)*2*pi / (high-low)
    res = np.mean(exp(1j*ang), axis=axis)
    R = abs(res)
    return ((high-low)/2.0/pi) * sqrt(-2*log(R))