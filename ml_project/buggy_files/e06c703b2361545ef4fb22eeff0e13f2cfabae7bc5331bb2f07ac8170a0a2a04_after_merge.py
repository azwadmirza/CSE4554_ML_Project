def nanargmax(a, axis=None):
    if a.dtype.kind == "O":
        fill_value = dtypes.get_neg_infinity(a.dtype)
        return _nan_argminmax_object("argmax", fill_value, a, axis=axis)

    module = dask_array if isinstance(a, dask_array_type) else nputils
    return module.nanargmax(a, axis=axis)