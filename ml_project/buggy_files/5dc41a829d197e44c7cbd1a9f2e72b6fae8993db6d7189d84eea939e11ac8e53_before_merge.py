def _coerce_to_type(x):
    """
    if the passed data is of datetime/timedelta type,
    this method converts it to integer so that cut method can
    handle it
    """
    dtype = None

    if is_timedelta64_dtype(x):
        x = to_timedelta(x).view(np.int64)
        dtype = np.timedelta64
    elif is_datetime64_dtype(x):
        x = to_datetime(x).view(np.int64)
        dtype = np.datetime64

    return x, dtype