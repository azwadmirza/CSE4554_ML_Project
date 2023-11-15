        def endswith_impl(a, b):
            a_offset = len(a) - len(b)
            if a_offset < 0:
                return False
            return _cmp_region(a, a_offset, b, 0, len(b)) == 0