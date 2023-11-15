def correlate(input, weights, output=None, mode='reflect', cval=0.0,
              origin=0):
    """
    Multidimensional correlation.

    The array is correlated with the given kernel.

    Parameters
    ----------
    %(input)s
    weights : ndarray
        array of weights, same number of dimensions as input
    %(output)s
    %(mode_multiple)s
    %(cval)s
    %(origin_multiple)s

    See Also
    --------
    convolve : Convolve an image with a kernel.
    """
    return _correlate_or_convolve(input, weights, output, mode, cval,
                                  origin, False)