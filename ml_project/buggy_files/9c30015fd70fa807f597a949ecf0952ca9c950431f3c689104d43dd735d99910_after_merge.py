def map_coordinates(input, coordinates, output=None, order=None,
                    mode='constant', cval=0.0, prefilter=True):
    """Map the input array to new coordinates by interpolation.

    The array of coordinates is used to find, for each point in the output, the
    corresponding coordinates in the input. The value of the input at those
    coordinates is determined by spline interpolation of the requested order.

    The shape of the output is derived from that of the coordinate array by
    dropping the first axis. The values of the array along the first axis are
    the coordinates in the input array at which the output value is found.

    Args:
        input (cupy.ndarray): The input array.
        coordinates (array_like): The coordinates at which ``input`` is
            evaluated.
        output (cupy.ndarray or ~cupy.dtype): The array in which to place the
            output, or the dtype of the returned array.
        order (int): The order of the spline interpolation. If it is not given,
            order 1 is used. It is different from :mod:`scipy.ndimage` and can
            change in the future. Currently it supports only order 0 and 1.
        mode (str): Points outside the boundaries of the input are filled
            according to the given mode (``'constant'``, ``'nearest'``,
            ``'mirror'`` or ``'opencv'``). Default is ``'constant'``.
        cval (scalar): Value used for points outside the boundaries of
            the input if ``mode='constant'`` or ``mode='opencv'``. Default is
            0.0
        prefilter (bool): It is not used yet. It just exists for compatibility
            with :mod:`scipy.ndimage`.

    Returns:
        cupy.ndarray:
            The result of transforming the input. The shape of the output is
            derived from that of ``coordinates`` by dropping the first axis.

    .. seealso:: :func:`scipy.ndimage.map_coordinates`
    """

    _check_parameter('map_coordinates', order, mode)

    if mode == 'opencv' or mode == '_opencv_edge':
        input = cupy.pad(input, [(1, 1)] * input.ndim, 'constant',
                         constant_values=cval)
        coordinates = cupy.add(coordinates, 1)
        mode = 'constant'

    ret = _util._get_output(output, input, coordinates.shape[1:])
    integer_output = ret.dtype.kind in 'iu'
    _util._check_cval(mode, cval, integer_output)

    if input.dtype.kind in 'iu':
        input = input.astype(cupy.float32)

    large_int = max(_prod(input.shape), coordinates.shape[0]) > 1 << 31
    kern = _interp_kernels._get_map_kernel(
        input.ndim, large_int, yshape=coordinates.shape, mode=mode, cval=cval,
        order=order, integer_output=integer_output)
    kern(input, coordinates, ret)
    return ret