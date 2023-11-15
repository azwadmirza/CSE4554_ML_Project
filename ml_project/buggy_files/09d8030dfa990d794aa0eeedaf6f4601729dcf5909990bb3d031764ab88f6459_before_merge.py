def unicode_rstrip(string, chars=None):

    if isinstance(chars, types.UnicodeCharSeq):
        def rstrip_impl(string, chars):
            return string.rstrip(str(chars))
        return rstrip_impl

    unicode_strip_types_check(chars)

    def rstrip_impl(string, chars=None):
        return string[:unicode_strip_right_bound(string, chars)]
    return rstrip_impl