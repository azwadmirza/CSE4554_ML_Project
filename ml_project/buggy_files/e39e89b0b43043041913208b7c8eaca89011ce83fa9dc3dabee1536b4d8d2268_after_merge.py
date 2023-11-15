def ignore_function(method=None, tracer=None):
    
    def inner(func):

        @functools.wraps(func)
        def ignore_wrapper(*args, **kwargs):
            # We need this to keep trace a local variable
            t = tracer
            if not t:
                t = get_tracer()
                if not t:
                    raise NameError("ignore_function only works with global tracer")
            t.pause()
            ret = func(*args, **kwargs)
            t.resume()
            return ret

        return ignore_wrapper

    if method:
        return inner(method)
    return inner 