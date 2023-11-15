def cumsum(a, axis=None, dtype=None, out=None):
    """Returns the cumulative sum of an array along a given axis.

    Args:
        a (cupy.ndarray): Input array.
        axis (int): Axis along which the cumulative sum is taken. If it is not
        specified, the input is flattened.
        dtype: Data type specifier.
        out (cupy.ndarray): Output array.

    Returns:
        cupy.ndarray: The result array.

    .. seealso:: :func:`numpy.cumsum`

    """
    if out is None:
        if dtype is None:
            kind = a.dtype.kind
            if kind == 'b':
                dtype = numpy.dtype('l')
            elif kind == 'i' and a.dtype.itemsize < numpy.dtype('l').itemsize:
                dtype = numpy.dtype('l')
            elif kind == 'u' and a.dtype.itemsize < numpy.dtype('L').itemsize:
                dtype = numpy.dtype('L')
            else:
                dtype = a.dtype

        out = a.astype(dtype)
    else:
        out[...] = a

    if axis is None:
        out = out.ravel()
    elif not (-a.ndim <= axis < a.ndim):
        raise core.core._AxisError('axis(={}) out of bounds'.format(axis))
    else:
        return _proc_as_batch(_cumsum_batch, out, axis=axis)

    kern = core.ElementwiseKernel(
        'int32 pos', 'raw T x',
        '''
        if (i & pos) {
          x[i] += x[i ^ pos | (pos - 1)];
        }
        ''',
        'cumsum_kernel'
    )

    pos = 1
    while pos < out.size:
        kern(pos, out, size=out.size)
        pos <<= 1
    return out