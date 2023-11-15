        def eq_impl(a, b):
            if len(a) != len(b):
                return False
            return _cmp_region(a, 0, b, 0, len(a)) == 0