    def register(cls, map_function, reduce_function, **kwargs):
        return cls.call(map_function, reduce_function, **kwargs)