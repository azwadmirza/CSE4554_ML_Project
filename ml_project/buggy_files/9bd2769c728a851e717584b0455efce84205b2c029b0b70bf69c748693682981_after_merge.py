def _get_positive_axis(ndim, axis):
    a = axis
    if a < 0:
        a += ndim
    if a < 0 or a >= ndim:
        raise core.core._AxisError(
            'axis {} out of bounds [0, {})'.format(axis, ndim))
    return a