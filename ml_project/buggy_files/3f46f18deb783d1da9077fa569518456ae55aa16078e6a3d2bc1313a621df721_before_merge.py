        def wrapped_func(self, **kwargs):
            return self.reduce(func, **kwargs)