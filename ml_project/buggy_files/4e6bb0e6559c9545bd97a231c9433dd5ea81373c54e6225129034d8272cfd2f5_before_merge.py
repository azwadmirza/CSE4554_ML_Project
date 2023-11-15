def qualname_from_frame(frame):
    """Get a qualified name for the code running in `frame`."""
    co = frame.f_code
    fname = co.co_name
    method = None
    if co.co_argcount and co.co_varnames[0] == "self":
        self = frame.f_locals["self"]
        method = getattr(self, fname, None)

    if method is None:
        func = frame.f_globals[fname]
        return func.__module__ + '.' + fname

    func = getattr(method, '__func__', None)
    if func is None:
        cls = self.__class__
        return cls.__module__ + '.' + cls.__name__ + "." + fname

    if hasattr(func, '__qualname__'):
        qname = func.__module__ + '.' + func.__qualname__
    else:
        for cls in getattr(self.__class__, '__mro__', ()):
            f = cls.__dict__.get(fname, None)
            if f is None:
                continue
            if f is func:
                qname = cls.__module__ + '.' + cls.__name__ + "." + fname
                break
        else:
            # Support for old-style classes.
            def mro(bases):
                for base in bases:
                    f = base.__dict__.get(fname, None)
                    if f is func:
                        return base.__module__ + '.' + base.__name__ + "." + fname
                for base in bases:
                    qname = mro(base.__bases__)
                    if qname is not None:
                        return qname
                return None
            qname = mro([self.__class__])
            if qname is None:
                qname = func.__module__ + '.' + fname

    return qname