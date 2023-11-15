def norm(x, ord=None, axis=None, keepdims=False):
    """Returns one of matrix norms specified by ``ord`` parameter.

    See numpy.linalg.norm for more detail.

    Args:
        x (cupy.ndarray): Array to take norm. If ``axis`` is None,
            ``x`` must be 1-D or 2-D.
        ord (non-zero int, inf, -inf, 'fro'): Norm type.
        axis (int, 2-tuple of ints, None): 1-D or 2-D norm is cumputed over
            ``axis``.
        keepdims (bool): If this is set ``True``, the axes which are normed
            over are left.

    Returns:
        cupy.ndarray

    """
    if not issubclass(x.dtype.type, numpy.inexact):
        x = x.astype(float)

    # Immediately handle some default, simple, fast, and common cases.
    if axis is None:
        ndim = x.ndim
        if (ord is None or (ndim == 1 and ord == 2) or
                (ndim == 2 and ord in ('f', 'fro'))):
            if x.dtype.kind == 'c':
                s = abs(x.ravel())
                s *= s
                ret = cupy.sqrt(s.sum())
            else:
                ret = cupy.sqrt((x * x).sum())
            if keepdims:
                ret = ret.reshape((1,) * ndim)
            return ret

    # Normalize the `axis` argument to a tuple.
    nd = x.ndim
    if axis is None:
        axis = tuple(range(nd))
    elif not isinstance(axis, tuple):
        try:
            axis = int(axis)
        except Exception:
            raise TypeError(
                '\'axis\' must be None, an integer or a tuple of integers')
        axis = (axis,)

    if len(axis) == 1:
        if ord == numpy.Inf:
            return abs(x).max(axis=axis, keepdims=keepdims)
        elif ord == -numpy.Inf:
            return abs(x).min(axis=axis, keepdims=keepdims)
        elif ord == 0:
            # Zero norm
            # Convert to Python float in accordance with NumPy
            return (x != 0).astype(x.real.dtype).sum(
                axis=axis, keepdims=keepdims)
        elif ord == 1:
            # special case for speedup
            return abs(x).sum(axis=axis, keepdims=keepdims)
        elif ord is None or ord == 2:
            # special case for speedup
            if x.dtype.kind == 'c':
                s = abs(x)
                s *= s
            else:
                s = x * x
            return cupy.sqrt(s.sum(axis=axis, keepdims=keepdims))
        else:
            try:
                float(ord)
            except TypeError:
                raise ValueError('Invalid norm order for vectors.')

            absx = abs(x)
            absx **= ord
            ret = absx.sum(axis=axis, keepdims=keepdims)
            ret **= cupy.reciprocal(ord, dtype=ret.dtype)
            return ret
    elif len(axis) == 2:
        row_axis, col_axis = axis
        if row_axis < 0:
            row_axis += nd
        if col_axis < 0:
            col_axis += nd
        if not (0 <= row_axis < nd and 0 <= col_axis < nd):
            raise ValueError('Invalid axis %r for an array with shape %r' %
                             (axis, x.shape))
        if row_axis == col_axis:
            raise ValueError('Duplicate axes given.')
        if ord == 2:
            op_max = functools.partial(cupy.take, indices=0)
            ret = _multi_svd_norm(x, row_axis, col_axis, op_max)
        elif ord == -2:
            op_min = functools.partial(cupy.take, indices=-1)
            ret = _multi_svd_norm(x, row_axis, col_axis, op_min)
        elif ord == 1:
            if col_axis > row_axis:
                col_axis -= 1
            ret = abs(x).sum(axis=row_axis).max(axis=col_axis)
        elif ord == numpy.Inf:
            if row_axis > col_axis:
                row_axis -= 1
            ret = abs(x).sum(axis=col_axis).max(axis=row_axis)
        elif ord == -1:
            if col_axis > row_axis:
                col_axis -= 1
            ret = abs(x).sum(axis=row_axis).min(axis=col_axis)
        elif ord == -numpy.Inf:
            if row_axis > col_axis:
                row_axis -= 1
            ret = abs(x).sum(axis=col_axis).min(axis=row_axis)
        elif ord in [None, 'fro', 'f']:
            if x.dtype.kind == 'c':
                s = abs(x)
                s *= s
                ret = cupy.sqrt(s.sum(axis=axis))
            else:
                ret = cupy.sqrt((x * x).sum(axis=axis))
        elif ord == 'nuc':
            ret = _multi_svd_norm(x, row_axis, col_axis, cupy.sum)
        else:
            raise ValueError('Invalid norm order for matrices.')
        if keepdims:
            ret_shape = list(x.shape)
            ret_shape[axis[0]] = 1
            ret_shape[axis[1]] = 1
            ret = ret.reshape(ret_shape)
        return ret
    else:
        raise ValueError('Improper number of dimensions to norm.')