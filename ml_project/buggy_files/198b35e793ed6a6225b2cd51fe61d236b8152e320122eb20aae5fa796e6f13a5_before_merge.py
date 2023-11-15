def pretty_error(func, *args, **kw):
    try:
        return func(*args, **kw)
    except (HyTypeError, LexException) as e:
        if SIMPLE_TRACEBACKS:
            sys.stderr.write(str(e))
            sys.exit(1)
        raise