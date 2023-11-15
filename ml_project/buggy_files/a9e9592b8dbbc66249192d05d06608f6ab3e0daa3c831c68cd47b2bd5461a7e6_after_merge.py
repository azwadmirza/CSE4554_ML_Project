def construct_1d_arraylike_from_scalar(
    value, length: int, dtype: DtypeObj
) -> ArrayLike:
    """
    create a np.ndarray / pandas type of specified shape and dtype
    filled with values

    Parameters
    ----------
    value : scalar value
    length : int
    dtype : pandas_dtype or np.dtype

    Returns
    -------
    np.ndarray / pandas type of length, filled with value

    """
    if is_extension_array_dtype(dtype):
        cls = dtype.construct_array_type()
        subarr = cls._from_sequence([value] * length, dtype=dtype)

    else:

        if length and is_integer_dtype(dtype) and isna(value):
            # coerce if we have nan for an integer dtype
            dtype = np.dtype("float64")
        elif isinstance(dtype, np.dtype) and dtype.kind in ("U", "S"):
            # we need to coerce to object dtype to avoid
            # to allow numpy to take our string as a scalar value
            dtype = np.dtype("object")
            if not isna(value):
                value = ensure_str(value)
        elif dtype.kind in ["M", "m"] and is_valid_nat_for_dtype(value, dtype):
            # GH36541: can't fill array directly with pd.NaT
            # > np.empty(10, dtype="datetime64[64]").fill(pd.NaT)
            # ValueError: cannot convert float NaN to integer
            value = np.datetime64("NaT")

        subarr = np.empty(length, dtype=dtype)
        subarr.fill(value)

    return subarr