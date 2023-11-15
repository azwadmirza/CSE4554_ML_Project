def _check_fill_value(fill_value, ndtype):
    """
    Private function validating the given `fill_value` for the given dtype.

    If fill_value is None, it is set to the default corresponding to the dtype
    if this latter is standard (no fields). If the datatype is flexible (named
    fields), fill_value is set to a tuple whose elements are the default fill
    values corresponding to each field.

    If fill_value is not None, its value is forced to the given dtype.

    """
    ndtype = np.dtype(ndtype)
    fields = ndtype.fields
    if fill_value is None:
        if fields:
            fill_value = np.array(_recursive_set_default_fill_value(ndtype),
                                  dtype=ndtype)
        else:
            fill_value = default_fill_value(ndtype)
    elif fields:
        fdtype = [(_[0], _[1]) for _ in ndtype.descr]
        if isinstance(fill_value, (ndarray, np.void)):
            try:
                fill_value = np.array(fill_value, copy=False, dtype=fdtype)
            except ValueError:
                err_msg = "Unable to transform %s to dtype %s"
                raise ValueError(err_msg % (fill_value, fdtype))
        else:
            fill_value = np.asarray(fill_value, dtype=object)
            fill_value = np.array(_recursive_set_fill_value(fill_value, ndtype),
                                  dtype=ndtype)
    else:
        if isinstance(fill_value, basestring) and (ndtype.char not in 'OSVU'):
            err_msg = "Cannot set fill value of string with array of dtype %s"
            raise TypeError(err_msg % ndtype)
        else:
            # In case we want to convert 1e20 to int.
            try:
                fill_value = np.array(fill_value, copy=False, dtype=ndtype)
            except OverflowError:
                # Raise TypeError instead of OverflowError. OverflowError
                # is seldom used, and the real problem here is that the
                # passed fill_value is not compatible with the ndtype.
                err_msg = "Fill value %s overflows dtype %s"
                raise TypeError(err_msg % (fill_value, ndtype))
    return np.array(fill_value)