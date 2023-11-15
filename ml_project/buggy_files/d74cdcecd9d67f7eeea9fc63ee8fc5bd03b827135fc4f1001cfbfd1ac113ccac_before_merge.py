def unicode_find(a, b):
    if isinstance(b, types.UnicodeType):
        def find_impl(a, b):
            return _find(substr=b, s=a)
        return find_impl