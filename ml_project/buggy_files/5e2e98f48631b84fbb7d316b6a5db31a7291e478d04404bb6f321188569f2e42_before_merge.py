def _get_take2d_function(dtype_str, axis=0):
    if axis == 0:
        return _take2d_axis0_dict[dtype_str]
    else:
        return _take2d_axis1_dict[dtype_str]