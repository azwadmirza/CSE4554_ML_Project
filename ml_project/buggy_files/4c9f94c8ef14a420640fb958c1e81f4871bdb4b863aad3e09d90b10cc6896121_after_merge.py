def iqr(x, axis=None, rng=(25, 75), scale='raw', nan_policy='propagate',
        interpolation='linear', keepdims=False):
    """
    Compute the interquartile range of the data along the specified axis.

    The interquartile range (IQR) is the difference between the 75th and
    25th percentile of the data. It is a measure of the dispersion
    similar to standard deviation or variance, but is much more robust
    against outliers [2]_.

    The ``rng`` parameter allows this function to compute other
    percentile ranges than the actual IQR. For example, setting
    ``rng=(0, 100)`` is equivalent to `numpy.ptp`.

    The IQR of an empty array is `np.nan`.

    .. versionadded:: 0.18.0

    Parameters
    ----------
    x : array_like
        Input array or object that can be converted to an array.
    axis : int or sequence of int, optional
        Axis along which the range is computed. The default is to
        compute the IQR for the entire array.
    rng : Two-element sequence containing floats in range of [0,100] optional
        Percentiles over which to compute the range. Each must be
        between 0 and 100, inclusive. The default is the true IQR:
        `(25, 75)`. The order of the elements is not important.
    scale : scalar or str, optional
        The numerical value of scale will be divided out of the final
        result. The following string values are recognized:

          'raw' : No scaling, just return the raw IQR.
          'normal' : Scale by :math:`2 \\sqrt{2} erf^{-1}(\\frac{1}{2}) \\approx 1.349`.

        The default is 'raw'. Array-like scale is also allowed, as long
        as it broadcasts correctly to the output such that
        ``out / scale`` is a valid operation. The output dimensions
        depend on the input array, `x`, the `axis` argument, and the
        `keepdims` flag.
    nan_policy : {'propagate', 'raise', 'omit'}, optional
        Defines how to handle when input contains nan. 'propagate'
        returns nan, 'raise' throws an error, 'omit' performs the
        calculations ignoring nan values. Default is 'propagate'.
    interpolation : {'linear', 'lower', 'higher', 'midpoint', 'nearest'}, optional
        Specifies the interpolation method to use when the percentile
        boundaries lie between two data points `i` and `j`:

          * 'linear' : `i + (j - i) * fraction`, where `fraction` is the
              fractional part of the index surrounded by `i` and `j`.
          * 'lower' : `i`.
          * 'higher' : `j`.
          * 'nearest' : `i` or `j` whichever is nearest.
          * 'midpoint' : `(i + j) / 2`.

        Default is 'linear'.
    keepdims : bool, optional
        If this is set to `True`, the reduced axes are left in the
        result as dimensions with size one. With this option, the result
        will broadcast correctly against the original array `x`.

    Returns
    -------
    iqr : scalar or ndarray
        If ``axis=None``, a scalar is returned. If the input contains
        integers or floats of smaller precision than ``np.float64``, then the
        output data-type is ``np.float64``. Otherwise, the output data-type is
        the same as that of the input.

    See Also
    --------
    numpy.std, numpy.var

    Examples
    --------
    >>> from scipy.stats import iqr
    >>> x = np.array([[10, 7, 4], [3, 2, 1]])
    >>> x
    array([[10,  7,  4],
           [ 3,  2,  1]])
    >>> iqr(x)
    4.0
    >>> iqr(x, axis=0)
    array([ 3.5,  2.5,  1.5])
    >>> iqr(x, axis=1)
    array([ 3.,  1.])
    >>> iqr(x, axis=1, keepdims=True)
    array([[ 3.],
           [ 1.]])

    Notes
    -----
    This function is heavily dependent on the version of `numpy` that is
    installed. Versions greater than 1.11.0b3 are highly recommended, as they
    include a number of enhancements and fixes to `numpy.percentile` and
    `numpy.nanpercentile` that affect the operation of this function. The
    following modifications apply:

    Below 1.10.0 : `nan_policy` is poorly defined.
        The default behavior of `numpy.percentile` is used for 'propagate'. This
        is a hybrid of 'omit' and 'propagate' that mostly yields a skewed
        version of 'omit' since NaNs are sorted to the end of the data. A
        warning is raised if there are NaNs in the data.
    Below 1.9.0: `numpy.nanpercentile` does not exist.
        This means that `numpy.percentile` is used regardless of `nan_policy`
        and a warning is issued. See previous item for a description of the
        behavior.
    Below 1.9.0: `keepdims` and `interpolation` are not supported.
        The keywords get ignored with a warning if supplied with non-default
        values. However, multiple axes are still supported.

    References
    ----------
    .. [1] "Interquartile range" https://en.wikipedia.org/wiki/Interquartile_range
    .. [2] "Robust measures of scale" https://en.wikipedia.org/wiki/Robust_measures_of_scale
    .. [3] "Quantile" https://en.wikipedia.org/wiki/Quantile
    """
    x = asarray(x)

    # This check prevents percentile from raising an error later. Also, it is
    # consistent with `np.var` and `np.std`.
    if not x.size:
        return np.nan

    # An error may be raised here, so fail-fast, before doing lengthy
    # computations, even though `scale` is not used until later
    if isinstance(scale, string_types):
        scale_key = scale.lower()
        if scale_key not in _scale_conversions:
            raise ValueError("{0} not a valid scale for `iqr`".format(scale))
        scale = _scale_conversions[scale_key]

    # Select the percentile function to use based on nans and policy
    contains_nan, nan_policy = _contains_nan(x, nan_policy)

    if contains_nan and nan_policy == 'omit':
        percentile_func = _iqr_nanpercentile
    else:
        percentile_func = _iqr_percentile

    if len(rng) != 2:
        raise TypeError("quantile range must be two element sequence")

    if np.isnan(rng).any():
        raise ValueError("range must not contain NaNs")

    rng = sorted(rng)
    pct = percentile_func(x, rng, axis=axis, interpolation=interpolation,
                          keepdims=keepdims, contains_nan=contains_nan)
    out = np.subtract(pct[1], pct[0])

    if scale != 1.0:
        out /= scale

    return out