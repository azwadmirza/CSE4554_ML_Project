        def _call(*args, **kwargs):
            gargs, gkwargs = g(*args, **kwargs)
            return f(*gargs, **gkwargs)