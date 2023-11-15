def _get_take2d_function(dtype_str, axis=0):
    if axis == 0:
        return _take2d_axis0_dict[dtype_str]
    elif axis == 1:
        return _take2d_axis1_dict[dtype_str]
    elif axis == 'multi':
        return _take2d_multi_dict[dtype_str]
    else: # pragma: no cover
        raise ValueError('bad axis: %s' % axis)