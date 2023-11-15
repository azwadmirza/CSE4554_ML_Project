    def rstrip_impl(string, chars=None):
        return string[:unicode_strip_right_bound(string, chars)]