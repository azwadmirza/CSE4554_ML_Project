def nan_to_num(x):
    """
    Replace nan with zero and inf with finite numbers.

    Returns an array or scalar replacing Not a Number (NaN) with zero,
    (positive) infinity with a very large number and negative infinity
    with a very small (or negative) number.

    Parameters
    ----------
    x : array_like
        Input data.

    Returns
    -------
    out : ndarray, float
        Array with the same shape as `x` and dtype of the element in `x`  with
        the greatest precision. NaN is replaced by zero, and infinity
        (-infinity) is replaced by the largest (smallest or most negative)
        floating point value that fits in the output dtype. All finite numbers
        are upcast to the output dtype (default float64).

    See Also
    --------
    isinf : Shows which elements are negative or negative infinity.
    isneginf : Shows which elements are negative infinity.
    isposinf : Shows which elements are positive infinity.
    isnan : Shows which elements are Not a Number (NaN).
    isfinite : Shows which elements are finite (not NaN, not infinity)

    Notes
    -----
    Numpy uses the IEEE Standard for Binary Floating-Point for Arithmetic
    (IEEE 754). This means that Not a Number is not equivalent to infinity.


    Examples
    --------
    >>> np.set_printoptions(precision=8)
    >>> x = np.array([np.inf, -np.inf, np.nan, -128, 128])
    >>> np.nan_to_num(x)
    array([  1.79769313e+308,  -1.79769313e+308,   0.00000000e+000,
            -1.28000000e+002,   1.28000000e+002])

    """
    try:
        t = x.dtype.type
    except AttributeError:
        t = obj2sctype(type(x))
    if issubclass(t, _nx.complexfloating):
        return nan_to_num(x.real) + 1j * nan_to_num(x.imag)
    else:
        try:
            y = x.copy()
        except AttributeError:
            y = array(x)
            t = y.dtype.type
    if not issubclass(t, _nx.integer):
        if not y.shape:
            y = array([x])
            scalar = True
        else:
            scalar = False
        are_inf = isposinf(y)
        are_neg_inf = isneginf(y)
        are_nan = isnan(y)
        maxf, minf = _getmaxmin(y.dtype.type)
        y[are_nan] = 0
        y[are_inf] = maxf
        y[are_neg_inf] = minf
        if scalar:
            y = y[0]
    return y