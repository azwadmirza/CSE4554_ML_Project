        def impl(*a, **kw):
            __tracebackhide__ = True
            params = func_parameters(func, *a, **kw)
            args, kwargs = params
            with StepContext(self.title.format(*args.values(), **kwargs), params):
                return func(*a, **kw)