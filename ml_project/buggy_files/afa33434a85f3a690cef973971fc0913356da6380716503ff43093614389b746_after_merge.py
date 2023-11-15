def where(condition, x=_NoValue, y=_NoValue):
    """
    Return a masked array with elements from x or y, depending on condition.

    Returns a masked array, shaped like condition, where the elements
    are from `x` when `condition` is True, and from `y` otherwise.
    If neither `x` nor `y` are given, the function returns a tuple of
    indices where `condition` is True (the result of
    ``condition.nonzero()``).

    Parameters
    ----------
    condition : array_like, bool
        The condition to meet. For each True element, yield the corresponding
        element from `x`, otherwise from `y`.
    x, y : array_like, optional
        Values from which to choose. `x` and `y` need to have the same shape
        as condition, or be broadcast-able to that shape.

    Returns
    -------
    out : MaskedArray or tuple of ndarrays
        The resulting masked array if `x` and `y` were given, otherwise
        the result of ``condition.nonzero()``.

    See Also
    --------
    numpy.where : Equivalent function in the top-level NumPy module.

    Examples
    --------
    >>> x = np.ma.array(np.arange(9.).reshape(3, 3), mask=[[0, 1, 0],
    ...                                                    [1, 0, 1],
    ...                                                    [0, 1, 0]])
    >>> print(x)
    [[0.0 -- 2.0]
     [-- 4.0 --]
     [6.0 -- 8.0]]
    >>> np.ma.where(x > 5)    # return the indices where x > 5
    (array([2, 2]), array([0, 2]))

    >>> print(np.ma.where(x > 5, x, -3.1416))
    [[-3.1416 -- -3.1416]
     [-- -3.1416 --]
     [6.0 -- 8.0]]

    """

    # handle the single-argument case
    missing = (x is _NoValue, y is _NoValue).count(True)
    if missing == 1:
        raise ValueError("Must provide both 'x' and 'y' or neither.")
    if missing == 2:
        return nonzero(condition)

    # we only care if the condition is true - false or masked pick y
    cf = filled(condition, False)
    xd = getdata(x)
    yd = getdata(y)

    # we need the full arrays here for correct final dimensions
    cm = getmaskarray(condition)
    xm = getmaskarray(x)
    ym = getmaskarray(y)

    # deal with the fact that masked.dtype == float64, but we don't actually
    # want to treat it as that.
    if x is masked and y is not masked:
        xd = np.zeros((), dtype=yd.dtype)
        xm = np.ones((),  dtype=ym.dtype)
    elif y is masked and x is not masked:
        yd = np.zeros((), dtype=xd.dtype)
        ym = np.ones((),  dtype=xm.dtype)

    data = np.where(cf, xd, yd)
    mask = np.where(cf, xm, ym)
    mask = np.where(cm, np.ones((), dtype=mask.dtype), mask)

    # collapse the mask, for backwards compatibility
    if mask.dtype == np.bool_ and not mask.any():
        mask = nomask

    return masked_array(data, mask=mask)