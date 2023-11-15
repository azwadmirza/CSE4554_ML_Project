    def _reduce_method(cls, func):
        def wrapped_func(self, **kwargs):
            return self.reduce(func, **kwargs)
        return wrapped_func