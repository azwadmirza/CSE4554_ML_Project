def unicode_lstrip(string, chars=None):
    unicode_strip_types_check(chars)

    def lstrip_impl(string, chars=None):
        return string[unicode_strip_left_bound(string, chars):]
    return lstrip_impl