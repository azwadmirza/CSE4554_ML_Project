    def __call__(self, a, *args, **params):
        if self.reversed:
            args = list(args)
            a, args[0] = args[0], a

        marr = asanyarray(a)
        method_name = self.__name__
        method = getattr(type(marr), method_name, None)
        if method is None:
            # use the corresponding np function
            method = getattr(np, method_name)

        return method(marr, *args, **params)