def unicode_eq(a, b):
    accept = (types.UnicodeType, types.StringLiteral, types.UnicodeCharSeq)
    a_unicode = isinstance(a, accept)
    b_unicode = isinstance(b, accept)
    if a_unicode and b_unicode:
        def eq_impl(a, b):
            if len(a) != len(b):
                return False
            return _cmp_region(a, 0, b, 0, len(a)) == 0
        return eq_impl
    elif a_unicode ^ b_unicode:
        # one of the things is unicode, everything compares False
        def eq_impl(a, b):
            return False
        return eq_impl