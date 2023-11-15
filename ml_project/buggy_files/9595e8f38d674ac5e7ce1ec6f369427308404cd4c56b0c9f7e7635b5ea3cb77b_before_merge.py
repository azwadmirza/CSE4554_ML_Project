def unicode_rstrip(string, chars=None):
    unicode_strip_types_check(chars)

    def rstrip_impl(string, chars=None):
        return string[:unicode_strip_right_bound(string, chars)]
    return rstrip_impl