        def ignore_wrapper(*args, **kwargs):
            tracer.pause()
            ret = func(*args, **kwargs)
            tracer.resume()
            return ret