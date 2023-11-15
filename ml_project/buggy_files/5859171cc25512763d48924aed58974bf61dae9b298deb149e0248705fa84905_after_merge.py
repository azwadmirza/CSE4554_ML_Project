    def __call__(self):
        """Wrap function for missing ``loc`` keyword argument.
        Otherwise, return the original *fn*.
        """
        fn = self.func
        if not _has_loc(fn):
            def wrapper(*args, **kwargs):
                kwargs.pop('loc')     # drop unused loc
                return fn(*args, **kwargs)

            # Copy the following attributes from the wrapped.
            # Following similar implementation as functools.wraps but
            # ignore attributes if not available (i.e fix py2.7)
            attrs = '__name__', 'libs'
            for attr in attrs:
                try:
                    val = getattr(fn, attr)
                except AttributeError:
                    pass
                else:
                    setattr(wrapper, attr, val)

            return wrapper
        else:
            return fn