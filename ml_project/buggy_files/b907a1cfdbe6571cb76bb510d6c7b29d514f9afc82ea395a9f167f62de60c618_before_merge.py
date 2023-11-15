        def impl(*a, **kw):
            __tracebackhide__ = True
            params = func_parameters(func, *a, **kw)
            with StepContext(self.title.format(*a, **kw), params):
                return func(*a, **kw)