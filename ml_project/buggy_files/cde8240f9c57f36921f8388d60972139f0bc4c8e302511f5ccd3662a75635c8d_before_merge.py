def unicode_ne(a, b):
    if isinstance(a, types.UnicodeType) and isinstance(b, types.UnicodeType):
        def ne_impl(a, b):
            return not (a == b)
        return ne_impl