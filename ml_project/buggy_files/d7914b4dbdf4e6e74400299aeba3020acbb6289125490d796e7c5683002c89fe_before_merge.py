def affine_transform(input, matrix, offset=0.0, output_shape=None, output=None,
                     order=None, mode='constant', cval=0.0, prefilter=True):
    """Apply an affine transformation.

    Given an output image pixel index vector ``o``, the pixel value is
    determined from the input image at position
    ``cupy.dot(matrix, o) + offset``.

    Args:
        input (cupy.ndarray): The input array.
        matrix (cupy.ndarray): The inverse coordinate transformation matrix,
            mapping output coordinates to input coordinates. If ``ndim`` is the
            number of dimensions of ``input``, the given matrix must have one
            of the following shapes:

                - ``(ndim, ndim)``: the linear transformation matrix for each
                  output coordinate.
                - ``(ndim,)``: assume that the 2D transformation matrix is
                  diagonal, with the diagonal specified by the given value.
                - ``(ndim + 1, ndim + 1)``: assume that the transformation is
                  specified using homogeneous coordinates. In this case, any
                  value passed to ``offset`` is ignored.
                - ``(ndim, ndim + 1)``: as above, but the bottom row of a
                  homogeneous transformation matrix is always
                  ``[0, 0, ..., 1]``, and may be omitted.

        offset (float or sequence): The offset into the array where the
            transform is applied. If a float, ``offset`` is the same for each
            axis. If a sequence, ``offset`` should contain one value for each
            axis.
        output_shape (tuple of ints): Shape tuple.
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
            The transformed input. If ``output`` is given as a parameter,
            ``None`` is returned.

    .. seealso:: :func:`scipy.ndimage.affine_transform`
    """

    _check_parameter('affine_transform', order, mode)

    offset = _util._fix_sequence_arg(offset, input.ndim, 'offset', float)

    if matrix.ndim not in [1, 2] or matrix.shape[0] < 1:
        raise RuntimeError('no proper affine matrix provided')
    if matrix.ndim == 2:
        if matrix.shape[0] == matrix.shape[1] - 1:
            offset = matrix[:, -1]
            matrix = matrix[:, :-1]
        elif matrix.shape[0] == input.ndim + 1:
            offset = matrix[:-1, -1]
            matrix = matrix[:-1, :-1]
        if matrix.shape != (input.ndim, input.ndim):
            raise RuntimeError("improper affine shape")

    if mode == 'opencv':
        m = cupy.zeros((input.ndim + 1, input.ndim + 1))
        m[:-1, :-1] = matrix
        m[:-1, -1] = offset
        m[-1, -1] = 1
        m = cupy.linalg.inv(m)
        m[:2] = cupy.roll(m[:2], 1, axis=0)
        m[:2, :2] = cupy.roll(m[:2, :2], 1, axis=1)
        matrix = m[:-1, :-1]
        offset = m[:-1, -1]

    if output_shape is None:
        output_shape = input.shape

    matrix = matrix.astype(cupy.float64, copy=False)
    if order is None:
        order = 1
    ndim = input.ndim
    output = _util._get_output(output, input, shape=output_shape)
    if input.dtype.kind in 'iu':
        input = input.astype(cupy.float32)

    integer_output = output.dtype.kind in 'iu'
    _util._check_cval(mode, cval, integer_output)
    large_int = max(_prod(input.shape), _prod(output_shape)) > 1 << 31
    if matrix.ndim == 1:
        offset = cupy.asarray(offset, dtype=cupy.float64)
        offset = -offset / matrix
        kern = _interp_kernels._get_zoom_shift_kernel(
            ndim, large_int, output_shape, mode, cval=cval, order=order,
            integer_output=integer_output)
        kern(input, offset, matrix, output)
    else:
        kern = _interp_kernels._get_affine_kernel(
            ndim, large_int, output_shape, mode, cval=cval, order=order,
            integer_output=integer_output)
        m = cupy.zeros((ndim, ndim + 1), dtype=cupy.float64)
        m[:, :-1] = matrix
        m[:, -1] = cupy.asarray(offset, dtype=cupy.float64)
        kern(input, m, output)
    return output