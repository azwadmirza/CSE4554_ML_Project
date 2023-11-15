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
    missing = (x is _NoValue, y is _NoValue).count(True)

    if missing == 1:
        raise ValueError("Must provide both 'x' and 'y' or neither.")
    if missing == 2:
        return filled(condition, 0).nonzero()

    # Both x and y are provided

    # Get the condition
    fc = filled(condition, 0).astype(MaskType)
    notfc = np.logical_not(fc)

    # Get the data
    xv = getdata(x)
    yv = getdata(y)
    if x is masked:
        ndtype = yv.dtype
    elif y is masked:
        ndtype = xv.dtype
    else:
        ndtype = np.find_common_type([xv.dtype, yv.dtype], [])

    # Construct an empty array and fill it
    d = np.empty(fc.shape, dtype=ndtype).view(MaskedArray)
    np.copyto(d._data, xv.astype(ndtype), where=fc)
    np.copyto(d._data, yv.astype(ndtype), where=notfc)

    # Create an empty mask and fill it
    mask = np.zeros(fc.shape, dtype=MaskType)
    np.copyto(mask, getmask(x), where=fc)
    np.copyto(mask, getmask(y), where=notfc)
    mask |= getmaskarray(condition)

    # Use d._mask instead of d.mask to avoid copies
    d._mask = mask if mask.any() else nomask

    return d