def unpack(g):
    def _unpack_inner(f):
        @functools.wraps(f)
        def _call(*args, **kwargs):
            gargs, gkwargs = g(*args, **kwargs)
            return f(*gargs, **gkwargs)
        return _call
    return _unpack_inner