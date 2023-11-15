def nanargmin(a, axis=None):
    fill_value = dtypes.get_pos_infinity(a.dtype)
    if a.dtype.kind == "O":
        return _nan_argminmax_object("argmin", fill_value, a, axis=axis)
    a, mask = _replace_nan(a, fill_value)
    if isinstance(a, dask_array_type):
        res = dask_array.argmin(a, axis=axis)
    else:
        res = np.argmin(a, axis=axis)

    if mask is not None:
        mask = mask.all(axis=axis)
        if mask.any():
            raise ValueError("All-NaN slice encountered")
    return res