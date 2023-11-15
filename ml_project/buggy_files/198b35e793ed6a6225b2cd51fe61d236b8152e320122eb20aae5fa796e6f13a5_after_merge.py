def pretty_error(func, *args, **kw):
    try:
        return func(*args, **kw)
    except (HyTypeError, LexException) as e:
        if SIMPLE_TRACEBACKS:
            print(e, file=sys.stderr)
            sys.exit(1)
        raise