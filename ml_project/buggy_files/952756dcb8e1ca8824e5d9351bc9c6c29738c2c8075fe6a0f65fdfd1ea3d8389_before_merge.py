def add_constant(data, prepend=False):
    '''
    This appends a column of ones to an array if prepend==False.

    For ndarrays and pandas.DataFrames, checks to make sure a constant is not
    already included. If there is at least one column of ones then the
    original object is returned.  Does not check for a constant if a structured
    or recarray is
    given.

    Parameters
    ----------
    data : array-like
        `data` is the column-ordered design matrix
    prepend : bool
        True and the constant is prepended rather than appended.

    Returns
    -------
    data : array
        The original array with a constant (column of ones) as the first or
        last column.

    Notes
    -----

    .. WARNING::
       The default of prepend will be changed to True in the next release of
       statsmodels. We recommend to use an explicit prepend in any permanent
       code.
    '''
    if not prepend:
        import inspect
        frame = inspect.currentframe().f_back
        info = inspect.getframeinfo(frame)
        try:
            to_warn = 'prepend' not in '\n'.join(info.code_context)
        except: # python 2.5 compatibility
            to_warn = 'prepend' not in '\n'.join(info[3])
        if to_warn:
            import warnings
            warnings.warn("The default of `prepend` will be changed to True "
                          "in 0.5.0, use explicit prepend",
                          FutureWarning)

    if _is_using_pandas(data, None):
        # work on a copy
        return _pandas_add_constant(data.copy(), prepend)
    else:
        data = np.asarray(data)
    if not data.dtype.names:
        var0 = data.var(0) == 0
        if np.any(var0):
            return data
        data = np.column_stack((data, np.ones((data.shape[0], 1))))
        if prepend:
            return np.roll(data, 1, 1)
    else:
        return_rec = data.__class__ is np.recarray
        if prepend:
            ones = np.ones((data.shape[0], 1), dtype=[('const', float)])
            data = nprf.append_fields(ones, data.dtype.names, [data[i] for
                i in data.dtype.names], usemask=False, asrecarray=return_rec)
        else:
            data = nprf.append_fields(data, 'const', np.ones(data.shape[0]),
                    usemask=False, asrecarray = return_rec)
    return data