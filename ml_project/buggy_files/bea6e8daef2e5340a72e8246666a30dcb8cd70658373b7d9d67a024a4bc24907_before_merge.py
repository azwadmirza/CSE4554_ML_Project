def isin(comps, values):
    """
    Compute the isin boolean array

    Parameters
    ----------
    comps: array-like
    values: array-like

    Returns
    -------
    boolean array same length as comps
    """

    if not is_list_like(comps):
        raise TypeError("only list-like objects are allowed to be passed"
                        " to isin(), you passed a "
                        "[{0}]".format(type(comps).__name__))
    if not is_list_like(values):
        raise TypeError("only list-like objects are allowed to be passed"
                        " to isin(), you passed a "
                        "[{0}]".format(type(values).__name__))

    if not isinstance(values, (ABCIndex, ABCSeries, np.ndarray)):
        values = lib.list_to_object_array(list(values))

    comps, dtype, _ = _ensure_data(comps)
    values, _, _ = _ensure_data(values, dtype=dtype)

    # GH11232
    # work-around for numpy < 1.8 and comparisions on py3
    # faster for larger cases to use np.in1d
    f = lambda x, y: htable.ismember_object(x, values)
    if (_np_version_under1p8 and compat.PY3) or len(comps) > 1000000:
        f = lambda x, y: np.in1d(x, y)
    elif is_integer_dtype(comps):
        try:
            values = values.astype('int64', copy=False)
            comps = comps.astype('int64', copy=False)
            f = lambda x, y: htable.ismember_int64(x, y)
        except (TypeError, ValueError):
            values = values.astype(object)
            comps = comps.astype(object)

    elif is_float_dtype(comps):
        try:
            values = values.astype('float64', copy=False)
            comps = comps.astype('float64', copy=False)
            checknull = isnull(values).any()
            f = lambda x, y: htable.ismember_float64(x, y, checknull)
        except (TypeError, ValueError):
            values = values.astype(object)
            comps = comps.astype(object)

    return f(comps, values)