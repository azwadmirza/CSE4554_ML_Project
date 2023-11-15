    def parse(self, handler, name=None):
        args, varargs, kwargs, defaults, kwonly, kwonlydefaults, annotations \
                = getfullargspec(unwrap(handler))
        if ismethod(handler) or handler.__name__ == '__init__':
            args = args[1:]  # drop 'self'
        spec = ArgumentSpec(
            name,
            self._type,
            positional=args,
            varargs=varargs,
            kwargs=kwargs,
            kwonlyargs=kwonly,
            defaults=self._get_defaults(args, defaults, kwonlydefaults)
        )
        spec.types = self._get_types(handler, annotations, spec)
        return spec