def tuple_hash(val):
    if _py38_or_later or isinstance(val, types.Sequence):
        def impl(val):
            return _tuple_hash(val)
        return impl
    else:
        def impl(val):
            hashed = _Py_hash_t(_tuple_hash_resolve(val))
            return process_return(hashed)
        return impl