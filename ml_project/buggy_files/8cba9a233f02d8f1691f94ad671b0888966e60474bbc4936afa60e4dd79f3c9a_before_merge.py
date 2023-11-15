def unicode_ge(a, b):
    if isinstance(a, types.UnicodeType) and isinstance(b, types.UnicodeType):
        def ge_impl(a, b):
            return not (a < b)
        return ge_impl