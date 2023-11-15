def maybe_cast_to_datetime(value, dtype, errors: str = "raise"):
    """
    try to cast the array/value to a datetimelike dtype, converting float
    nan to iNaT
    """
    from pandas.core.tools.timedeltas import to_timedelta
    from pandas.core.tools.datetimes import to_datetime

    if dtype is not None:
        if isinstance(dtype, str):
            dtype = np.dtype(dtype)

        is_datetime64 = is_datetime64_dtype(dtype)
        is_datetime64tz = is_datetime64tz_dtype(dtype)
        is_timedelta64 = is_timedelta64_dtype(dtype)

        if is_datetime64 or is_datetime64tz or is_timedelta64:

            # Force the dtype if needed.
            msg = (
                f"The '{dtype.name}' dtype has no unit. "
                f"Please pass in '{dtype.name}[ns]' instead."
            )

            if is_datetime64 and not is_dtype_equal(dtype, DT64NS_DTYPE):

                # pandas supports dtype whose granularity is less than [ns]
                # e.g., [ps], [fs], [as]
                if dtype <= np.dtype("M8[ns]"):
                    if dtype.name == "datetime64":
                        raise ValueError(msg)
                    dtype = DT64NS_DTYPE
                else:
                    raise TypeError(f"cannot convert datetimelike to dtype [{dtype}]")
            elif is_datetime64tz:

                # our NaT doesn't support tz's
                # this will coerce to DatetimeIndex with
                # a matching dtype below
                if is_scalar(value) and isna(value):
                    value = [value]

            elif is_timedelta64 and not is_dtype_equal(dtype, TD64NS_DTYPE):

                # pandas supports dtype whose granularity is less than [ns]
                # e.g., [ps], [fs], [as]
                if dtype <= np.dtype("m8[ns]"):
                    if dtype.name == "timedelta64":
                        raise ValueError(msg)
                    dtype = TD64NS_DTYPE
                else:
                    raise TypeError(f"cannot convert timedeltalike to dtype [{dtype}]")

            if is_scalar(value):
                if value == iNaT or isna(value):
                    value = iNaT
            else:
                value = np.array(value, copy=False)

                # have a scalar array-like (e.g. NaT)
                if value.ndim == 0:
                    value = iNaT

                # we have an array of datetime or timedeltas & nulls
                elif np.prod(value.shape) or not is_dtype_equal(value.dtype, dtype):
                    try:
                        if is_datetime64:
                            value = to_datetime(value, errors=errors)
                            # GH 25843: Remove tz information since the dtype
                            # didn't specify one
                            if value.tz is not None:
                                value = value.tz_localize(None)
                            value = value._values
                        elif is_datetime64tz:
                            # The string check can be removed once issue #13712
                            # is solved. String data that is passed with a
                            # datetime64tz is assumed to be naive which should
                            # be localized to the timezone.
                            is_dt_string = is_string_dtype(value)
                            value = to_datetime(value, errors=errors).array
                            if is_dt_string:
                                # Strings here are naive, so directly localize
                                value = value.tz_localize(dtype.tz)
                            else:
                                # Numeric values are UTC at this point,
                                # so localize and convert
                                value = value.tz_localize("UTC").tz_convert(dtype.tz)
                        elif is_timedelta64:
                            value = to_timedelta(value, errors=errors)._values
                    except OutOfBoundsDatetime:
                        raise
                    except (AttributeError, ValueError, TypeError):
                        pass

        # coerce datetimelike to object
        elif is_datetime64_dtype(value) and not is_datetime64_dtype(dtype):
            if is_object_dtype(dtype):
                if value.dtype != DT64NS_DTYPE:
                    value = value.astype(DT64NS_DTYPE)
                ints = np.asarray(value).view("i8")
                return tslib.ints_to_pydatetime(ints)

            # we have a non-castable dtype that was passed
            raise TypeError(f"Cannot cast datetime64 to {dtype}")

    else:

        is_array = isinstance(value, np.ndarray)

        # catch a datetime/timedelta that is not of ns variety
        # and no coercion specified
        if is_array and value.dtype.kind in ["M", "m"]:
            dtype = value.dtype

            if dtype.kind == "M" and dtype != DT64NS_DTYPE:
                value = tslibs.conversion.ensure_datetime64ns(value)

            elif dtype.kind == "m" and dtype != TD64NS_DTYPE:
                value = to_timedelta(value)

        # only do this if we have an array and the dtype of the array is not
        # setup already we are not an integer/object, so don't bother with this
        # conversion
        elif not (
            is_array
            and not (
                issubclass(value.dtype.type, np.integer) or value.dtype == np.object_
            )
        ):
            value = maybe_infer_to_datetimelike(value)

    return value