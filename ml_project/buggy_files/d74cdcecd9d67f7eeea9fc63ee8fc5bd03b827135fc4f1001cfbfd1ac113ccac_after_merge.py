def unicode_find(a, b):
    if isinstance(b, types.UnicodeType):
        def find_impl(a, b):
            return _find(substr=b, s=a)
        return find_impl
    if isinstance(b, types.UnicodeCharSeq):
        def find_impl(a, b):
            return a.find(str(b))
        return find_impl