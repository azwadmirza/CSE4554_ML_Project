def _check_fill_value(fill_value, ndtype):
    """
    Private function validating the given `fill_value` for the given dtype.

    If fill_value is None, it is set to the default corresponding to the dtype.

    If fill_value is not None, its value is forced to the given dtype.

    The result is always a 0d array.

    """
    ndtype = np.dtype(ndtype)
    fields = ndtype.fields
    if fill_value is None:
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
            # Note this check doesn't work if fill_value is not a scalar
            err_msg = "Cannot set fill value of string with array of dtype %s"
            raise TypeError(err_msg % ndtype)
        else:
            # In case we want to convert 1e20 to int.
            # Also in case of converting string arrays.
            try:
                fill_value = np.array(fill_value, copy=False, dtype=ndtype)
            except (OverflowError, ValueError):
                # Raise TypeError instead of OverflowError or ValueError.
                # OverflowError is seldom used, and the real problem here is
                # that the passed fill_value is not compatible with the ndtype.
                err_msg = "Cannot convert fill_value %s to dtype %s"
                raise TypeError(err_msg % (fill_value, ndtype))
    return np.array(fill_value)