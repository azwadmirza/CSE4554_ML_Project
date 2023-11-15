def ignore_function(method=None, tracer=None):
    if not tracer:
        tracer = get_tracer()
    
    def inner(func):

        @functools.wraps(func)
        def ignore_wrapper(*args, **kwargs):
            tracer.pause()
            ret = func(*args, **kwargs)
            tracer.resume()
            return ret

        return ignore_wrapper

    if method:
        return inner(method)
    return inner 