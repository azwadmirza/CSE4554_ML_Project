def _ensure_data(values, dtype=None):
    """
    routine to ensure that our data is of the correct
    input dtype for lower-level routines

    This will coerce:
    - ints -> int64
    - uint -> uint64
    - bool -> uint64 (TODO this should be uint8)
    - datetimelike -> i8
    - datetime64tz -> i8 (in local tz)
    - categorical -> codes

    Parameters
    ----------
    values : array-like
    dtype : pandas_dtype, optional
        coerce to this dtype

    Returns
    -------
    (ndarray, pandas_dtype, algo dtype as a string)

    """

    # we check some simple dtypes first
    try:
        if is_object_dtype(dtype):
            return ensure_object(np.asarray(values)), 'object', 'object'
        if is_bool_dtype(values) or is_bool_dtype(dtype):
            # we are actually coercing to uint64
            # until our algos support uint8 directly (see TODO)
            return np.asarray(values).astype('uint64'), 'bool', 'uint64'
        elif is_signed_integer_dtype(values) or is_signed_integer_dtype(dtype):
            return ensure_int64(values), 'int64', 'int64'
        elif (is_unsigned_integer_dtype(values) or
              is_unsigned_integer_dtype(dtype)):
            return ensure_uint64(values), 'uint64', 'uint64'
        elif is_float_dtype(values) or is_float_dtype(dtype):
            return ensure_float64(values), 'float64', 'float64'
        elif is_object_dtype(values) and dtype is None:
            return ensure_object(np.asarray(values)), 'object', 'object'
        elif is_complex_dtype(values) or is_complex_dtype(dtype):

            # ignore the fact that we are casting to float
            # which discards complex parts
            with catch_warnings(record=True):
                values = ensure_float64(values)
            return values, 'float64', 'float64'

    except (TypeError, ValueError):
        # if we are trying to coerce to a dtype
        # and it is incompat this will fall thru to here
        return ensure_object(values), 'object', 'object'

    # datetimelike
    if (needs_i8_conversion(values) or
            is_period_dtype(dtype) or
            is_datetime64_any_dtype(dtype) or
            is_timedelta64_dtype(dtype)):
        if is_period_dtype(values) or is_period_dtype(dtype):
            from pandas import PeriodIndex
            values = PeriodIndex(values)
            dtype = values.dtype
        elif is_timedelta64_dtype(values) or is_timedelta64_dtype(dtype):
            from pandas import TimedeltaIndex
            values = TimedeltaIndex(values)
            dtype = values.dtype
        else:
            # Datetime
            from pandas import DatetimeIndex
            values = DatetimeIndex(values)
            dtype = values.dtype

        return values.asi8, dtype, 'int64'

    elif (is_categorical_dtype(values) and
          (is_categorical_dtype(dtype) or dtype is None)):
        values = getattr(values, 'values', values)
        values = values.codes
        dtype = 'category'

        # we are actually coercing to int64
        # until our algos support int* directly (not all do)
        values = ensure_int64(values)

        return values, dtype, 'int64'

    # we have failed, return object
    values = np.asarray(values)
    return ensure_object(values), 'object', 'object'