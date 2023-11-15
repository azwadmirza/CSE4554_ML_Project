def unicode_lstrip(string, chars=None):

    if isinstance(chars, types.UnicodeCharSeq):
        def lstrip_impl(string, chars):
            return string.lstrip(str(chars))
        return lstrip_impl

    unicode_strip_types_check(chars)

    def lstrip_impl(string, chars=None):
        return string[unicode_strip_left_bound(string, chars):]
    return lstrip_impl