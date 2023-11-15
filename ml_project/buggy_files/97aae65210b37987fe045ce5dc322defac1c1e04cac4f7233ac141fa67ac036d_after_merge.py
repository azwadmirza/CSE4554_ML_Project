def unicode_strip(string, chars=None):

    if isinstance(chars, types.UnicodeCharSeq):
        def strip_impl(string, chars):
            return string.strip(str(chars))
        return strip_impl

    unicode_strip_types_check(chars)

    def strip_impl(string, chars=None):
        lb = unicode_strip_left_bound(string, chars)
        rb = unicode_strip_right_bound(string, chars)
        return string[lb:rb]
    return strip_impl