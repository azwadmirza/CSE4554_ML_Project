def unicode_strip(string, chars=None):
    unicode_strip_types_check(chars)

    def strip_impl(string, chars=None):
        lb = unicode_strip_left_bound(string, chars)
        rb = unicode_strip_right_bound(string, chars)
        return string[lb:rb]
    return strip_impl