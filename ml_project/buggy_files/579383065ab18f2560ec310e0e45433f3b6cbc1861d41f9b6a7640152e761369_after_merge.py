def unicode_startswith(a, b):
    if isinstance(b, types.UnicodeType):
        def startswith_impl(a, b):
            return _cmp_region(a, 0, b, 0, len(b)) == 0
        return startswith_impl
    if isinstance(b, types.UnicodeCharSeq):
        def startswith_impl(a, b):
            return a.startswith(str(b))
        return startswith_impl