def nanargmin(a, axis=None):
    if a.dtype.kind == "O":
        fill_value = dtypes.get_pos_infinity(a.dtype)
        return _nan_argminmax_object("argmin", fill_value, a, axis=axis)

    module = dask_array if isinstance(a, dask_array_type) else nputils
    return module.nanargmin(a, axis=axis)