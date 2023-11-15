def global_injector_decorator(inject_globals):
    '''
    Decorator used by the LazyLoader to inject globals into a function at
    execute time.

    globals
        Dictionary with global variables to inject
    '''
    def inner_decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            with context.func_globals_inject(f, **inject_globals):
                return f(*args, **kwargs)
        return wrapper
    return inner_decorator