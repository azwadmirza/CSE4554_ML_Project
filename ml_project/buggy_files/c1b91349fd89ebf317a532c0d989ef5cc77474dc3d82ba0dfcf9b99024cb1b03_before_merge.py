def match(values, index):
    """


    Parameters
    ----------

    Returns
    -------
    match : ndarray
    """
    if com.is_float_dtype(index):
        return _match_generic(values, index, lib.Float64HashTable,
                              com._ensure_float64)
    elif com.is_integer_dtype(index):
        return _match_generic(values, index, lib.Int64HashTable,
                              com._ensure_int64)
    else:
        return _match_generic(values, index, lib.PyObjectHashTable,
                              com._ensure_object)