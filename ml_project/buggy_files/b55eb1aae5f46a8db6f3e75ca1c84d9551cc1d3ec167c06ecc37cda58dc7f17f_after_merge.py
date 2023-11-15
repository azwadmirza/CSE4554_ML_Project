def unicode_endswith(a, b):
    if isinstance(b, types.UnicodeType):
        def endswith_impl(a, b):
            a_offset = len(a) - len(b)
            if a_offset < 0:
                return False
            return _cmp_region(a, a_offset, b, 0, len(b)) == 0
        return endswith_impl
    if isinstance(b, types.UnicodeCharSeq):
        def endswith_impl(a, b):
            return a.endswith(str(b))
        return endswith_impl