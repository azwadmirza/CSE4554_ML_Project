def unicode_ne(a, b):
    accept = (types.UnicodeType, types.StringLiteral, types.UnicodeCharSeq)
    a_unicode = isinstance(a, accept)
    b_unicode = isinstance(b, accept)
    if a_unicode and b_unicode:
        def ne_impl(a, b):
            return not (a == b)
        return ne_impl
    elif a_unicode ^ b_unicode:
        # one of the things is unicode, everything compares True
        def eq_impl(a, b):
            return True
        return eq_impl