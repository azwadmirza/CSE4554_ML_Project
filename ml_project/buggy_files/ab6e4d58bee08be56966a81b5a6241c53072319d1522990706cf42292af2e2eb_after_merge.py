def white_tophat(input, size=None, footprint=None, structure=None,
                 output=None, mode="reflect", cval=0.0, origin=0):
    """
    Multi-dimensional white tophat filter.

    Parameters
    ----------
    input : array_like
        Input.
    size : tuple of ints
        Shape of a flat and full structuring element used for the filter.
        Optional if `footprint` or `structure` is provided.
    footprint : array of ints, optional
        Positions of elements of a flat structuring element
        used for the white tophat filter.
    structure : array of ints, optional
        Structuring element used for the filter. `structure`
        may be a non-flat structuring element.
    output : array, optional
        An array used for storing the output of the filter may be provided.
    mode : {'reflect', 'constant', 'nearest', 'mirror', 'wrap'}, optional
        The `mode` parameter determines how the array borders are
        handled, where `cval` is the value when mode is equal to
        'constant'. Default is 'reflect'
    cval : scalar, optional
        Value to fill past edges of input if `mode` is 'constant'.
        Default is 0.0.
    origin : scalar, optional
        The `origin` parameter controls the placement of the filter.
        Default is 0.

    Returns
    -------
    output : ndarray
        Result of the filter of `input` with `structure`.

    See also
    --------
    black_tophat

    """
    tmp = grey_erosion(input, size, footprint, structure, None, mode,
                       cval, origin)
    tmp = grey_dilation(tmp, size, footprint, structure, output, mode,
                        cval, origin)
    if tmp is None:
        tmp = output

    if input.dtype == numpy.bool_ and tmp.dtype == numpy.bool_:
        numpy.bitwise_xor(input, tmp, out=tmp)
    else:
        numpy.subtract(input, tmp, out=tmp)
    return tmp