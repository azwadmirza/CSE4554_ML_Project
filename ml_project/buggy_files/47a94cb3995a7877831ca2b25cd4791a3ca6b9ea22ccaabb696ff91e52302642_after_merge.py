def isnull(obj):
    '''
    Replacement for numpy.isnan / -numpy.isfinite which is suitable
    for use on object arrays.

    Parameters
    ----------
    arr: ndarray or object value

    Returns
    -------
    boolean ndarray or boolean
    '''
    if lib.isscalar(obj):
        return lib.checknull(obj)

    from pandas.core.generic import PandasObject
    from pandas import Series
    if isinstance(obj, np.ndarray):
        if obj.dtype.kind in ('O', 'S'):
            # Working around NumPy ticket 1542
            shape = obj.shape
            result = np.empty(shape, dtype=bool)
            vec = lib.isnullobj(obj.ravel())
            result[:] = vec.reshape(shape)

            if isinstance(obj, Series):
                result = Series(result, index=obj.index, copy=False)
        elif obj.dtype == np.dtype('M8[ns]'):
            # this is the NaT pattern
            result = np.array(obj).view('i8') == lib.iNaT
        else:
            result = -np.isfinite(obj)
        return result
    elif isinstance(obj, PandasObject):
        # TODO: optimize for DataFrame, etc.
        return obj.apply(isnull)
    else:
        return obj is None