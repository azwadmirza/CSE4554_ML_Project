def unicode_le(a, b):
    if isinstance(a, types.UnicodeType) and isinstance(b, types.UnicodeType):
        def le_impl(a, b):
            return not (a > b)
        return le_impl