def _validate_usecols_arg(usecols):
    """
    Check whether or not the 'usecols' parameter
    contains all integers (column selection by index)
    or strings (column by name). Raises a ValueError
    if that is not the case.
    """
    msg = ("The elements of 'usecols' must "
           "either be all strings, all unicode, or all integers")

    if usecols is not None:
        usecols_dtype = lib.infer_dtype(usecols)
        if usecols_dtype not in ('empty', 'integer',
                                 'string', 'unicode'):
            raise ValueError(msg)

        return set(usecols)
    return usecols