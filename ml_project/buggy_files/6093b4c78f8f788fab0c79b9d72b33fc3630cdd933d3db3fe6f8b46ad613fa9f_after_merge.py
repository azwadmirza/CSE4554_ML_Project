    def register(cls, map_function, reduce_function=None, **kwargs):
        if reduce_function is None:
            reduce_function = map_function
        return cls.call(map_function, reduce_function, **kwargs)