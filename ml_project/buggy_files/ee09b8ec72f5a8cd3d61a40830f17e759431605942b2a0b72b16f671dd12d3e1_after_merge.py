def unicode_lt(a, b):
    a_unicode = isinstance(a, (types.UnicodeType, types.StringLiteral))
    b_unicode = isinstance(b, (types.UnicodeType, types.StringLiteral))
    if a_unicode and b_unicode:
        def lt_impl(a, b):
            minlen = min(len(a), len(b))
            eqcode = _cmp_region(a, 0, b, 0, minlen)
            if eqcode == -1:
                return True
            elif eqcode == 0:
                return len(a) < len(b)
            return False
        return lt_impl