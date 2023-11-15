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
                        " to isin(), you passed a [{comps_type}]"
                        .format(comps_type=type(comps).__name__))
    if not is_list_like(values):
        raise TypeError("only list-like objects are allowed to be passed"
                        " to isin(), you passed a [{values_type}]"
                        .format(values_type=type(values).__name__))

    if not isinstance(values, (ABCIndex, ABCSeries, np.ndarray)):
        values = construct_1d_object_array_from_listlike(list(values))

    if is_categorical_dtype(comps):
        # TODO(extension)
        # handle categoricals
        return comps._values.isin(values)

    comps = com.values_from_object(comps)

    comps, dtype, _ = _ensure_data(comps)
    values, _, _ = _ensure_data(values, dtype=dtype)

    # faster for larger cases to use np.in1d
    f = lambda x, y: htable.ismember_object(x, values)

    # GH16012
    # Ensure np.in1d doesn't get object types or it *may* throw an exception
    if len(comps) > 1000000 and not is_object_dtype(comps):
        f = lambda x, y: np.in1d(x, y)
    elif is_integer_dtype(comps):
        try:
            values = values.astype('int64', copy=False)
            comps = comps.astype('int64', copy=False)
            f = lambda x, y: htable.ismember_int64(x, y)
        except (TypeError, ValueError, OverflowError):
            values = values.astype(object)
            comps = comps.astype(object)

    elif is_float_dtype(comps):
        try:
            values = values.astype('float64', copy=False)
            comps = comps.astype('float64', copy=False)
            checknull = isna(values).any()
            f = lambda x, y: htable.ismember_float64(x, y, checknull)
        except (TypeError, ValueError):
            values = values.astype(object)
            comps = comps.astype(object)

    return f(comps, values)