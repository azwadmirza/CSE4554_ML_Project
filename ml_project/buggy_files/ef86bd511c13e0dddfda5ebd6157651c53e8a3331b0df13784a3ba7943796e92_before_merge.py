def _nanmin(values, axis=None, skipna=True):
    mask = isnull(values)
    if skipna and not issubclass(values.dtype.type,
                                 (np.integer, np.datetime64)):
        values = values.copy()
        np.putmask(values, mask, np.inf)
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
        result = values.min(axis)

    return _maybe_null_out(result, axis, mask)