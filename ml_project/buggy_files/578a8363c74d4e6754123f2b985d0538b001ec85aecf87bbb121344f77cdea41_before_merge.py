def _nanmin(values, axis=None, skipna=True):
    mask = isnull(values)

    dtype = values.dtype

    if skipna and not issubclass(dtype.type,
                                 (np.integer, np.datetime64)):
        values = values.copy()
        np.putmask(values, mask, np.inf)

    if issubclass(dtype.type, np.datetime64):
        values = values.view(np.int64)

    # numpy 1.6.1 workaround in Python 3.x
    if (values.dtype == np.object_
        and sys.version_info[0] >= 3):  # pragma: no cover
        import __builtin__
        if values.ndim > 1:
            apply_ax = axis if axis is not None else 0
            result = np.apply_along_axis(__builtin__.min, apply_ax, values)
        else:
            result = __builtin__.min(values)
    else:
        if ((axis is not None and values.shape[axis] == 0)
             or values.size == 0):
            result = values.sum(axis)
            result.fill(np.nan)
        else:
            result = values.min(axis)

    if issubclass(dtype.type, np.datetime64):
        if not isinstance(result, np.ndarray):
            result = lib.Timestamp(result)
        else:
            result = result.view(dtype)

    return _maybe_null_out(result, axis, mask)