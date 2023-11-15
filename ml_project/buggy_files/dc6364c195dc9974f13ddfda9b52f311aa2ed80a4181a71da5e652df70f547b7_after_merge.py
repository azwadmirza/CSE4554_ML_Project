def _nanvar(values, axis=None, skipna=True, ddof=1):
    mask = isnull(values)

    if axis is not None:
        count = (values.shape[axis] - mask.sum(axis)).astype(float)
    else:
        count = float(values.size - mask.sum())

    if skipna:
        values = values.copy()
        np.putmask(values, mask, 0)

    X = _ensure_numeric(values.sum(axis))
    XX = _ensure_numeric((values ** 2).sum(axis))
    return np.fabs((XX - X ** 2 / count) / (count - ddof))