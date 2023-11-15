    def inner(func):

        @functools.wraps(func)
        def ignore_wrapper(*args, **kwargs):
            tracer.pause()
            ret = func(*args, **kwargs)
            tracer.resume()
            return ret

        return ignore_wrapper