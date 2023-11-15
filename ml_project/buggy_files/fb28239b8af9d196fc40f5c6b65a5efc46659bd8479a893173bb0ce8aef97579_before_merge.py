    def register(self, type_class):
        """
        Register a LLVM type factory function for the given *type_class*
        (i.e. a subclass of numba.types.Type).
        """
        assert issubclass(type_class, types.Type)
        def decorator(func):
            self.factories[type_class] = func
            return func
        return decorator