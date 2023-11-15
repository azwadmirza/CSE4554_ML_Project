def shift(input, shift, output=None, order=None, mode='constant', cval=0.0,
          prefilter=True):
    """Shift an array.

    The array is shifted using spline interpolation of the requested order.
    Points outside the boundaries of the input are filled according to the
    given mode.

    Args:
        input (cupy.ndarray): The input array.
        shift (float or sequence): The shift along the axes. If a float,
            ``shift`` is the same for each axis. If a sequence, ``shift``
            should contain one value for each axis.
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
        cupy.ndarray or None:
            The shifted input.

    .. seealso:: :func:`scipy.ndimage.shift`
    """

    _check_parameter('shift', order, mode)

    shift = _util._fix_sequence_arg(shift, input.ndim, 'shift', float)

    if mode == 'opencv':
        mode = '_opencv_edge'

        output = affine_transform(
            input,
            cupy.ones(input.ndim, input.dtype),
            cupy.negative(cupy.asarray(shift)),
            None,
            output,
            order,
            mode,
            cval,
            prefilter,
        )
    else:
        if order is None:
            order = 1
        output = _util._get_output(output, input)
        if input.dtype.kind in 'iu':
            input = input.astype(cupy.float32)
        integer_output = output.dtype.kind in 'iu'
        large_int = _prod(input.shape) > 1 << 31
        kern = _interp_kernels._get_shift_kernel(
            input.ndim, large_int, input.shape, mode, cval=cval, order=order,
            integer_output=integer_output)
        shift = cupy.asarray(shift, dtype=cupy.float64)
        kern(input, shift, output)
    return output