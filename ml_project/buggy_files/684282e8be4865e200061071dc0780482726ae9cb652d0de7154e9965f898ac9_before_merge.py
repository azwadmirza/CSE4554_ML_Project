def count(values, uniques=None):
    if uniques is not None:
        raise NotImplementedError
    else:
        if com.is_float_dtype(values):
            return _count_generic(values, lib.Float64HashTable,
                                  com._ensure_float64)
        elif com.is_integer_dtype(values):
            return _count_generic(values, lib.Int64HashTable,
                                  com._ensure_int64)
        else:
            return _count_generic(values, lib.PyObjectHashTable,
                                  com._ensure_object)