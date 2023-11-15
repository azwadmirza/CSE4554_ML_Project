def unicode_ge(a, b):
    a_unicode = isinstance(a, (types.UnicodeType, types.StringLiteral))
    b_unicode = isinstance(b, (types.UnicodeType, types.StringLiteral))
    if a_unicode and b_unicode:
        def ge_impl(a, b):
            return not (a < b)
        return ge_impl