        def startswith_impl(a, b):
            return _cmp_region(a, 0, b, 0, len(b)) == 0