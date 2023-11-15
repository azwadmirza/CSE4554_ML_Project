def _isnull_ndarraylike(obj):
    from pandas import Series
    values = np.asarray(obj)

    if values.dtype.kind in ('O', 'S', 'U'):
        # Working around NumPy ticket 1542
        shape = values.shape

        if values.dtype.kind in ('S', 'U'):
            result = np.zeros(values.shape, dtype=bool)
        else:
            result = np.empty(shape, dtype=bool)
            vec = lib.isnullobj(values.ravel())
            result[:] = vec.reshape(shape)

        if isinstance(obj, Series):
            result = Series(result, index=obj.index, copy=False)
    elif values.dtype == np.dtype('M8[ns]'):
        # this is the NaT pattern
        result = values.view('i8') == lib.iNaT
    else:
        result = -np.isfinite(obj)
    return result