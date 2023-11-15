    def lstrip_impl(string, chars=None):
        return string[unicode_strip_left_bound(string, chars):]