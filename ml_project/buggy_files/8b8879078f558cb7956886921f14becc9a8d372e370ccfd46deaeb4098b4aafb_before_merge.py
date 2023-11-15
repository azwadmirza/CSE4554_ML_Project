    def _unpack_inner(f):
        @functools.wraps(f)
        def _call(**kwargs):
            return f(**g(**kwargs))
        return _call