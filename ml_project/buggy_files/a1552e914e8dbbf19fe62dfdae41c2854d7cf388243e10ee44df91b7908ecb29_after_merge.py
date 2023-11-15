    def parse(self, handler, name=None):
        args, varargs, kws, defaults, kwo, kwo_defaults, annotations \
                = self._get_arg_spec(handler)
        spec = ArgumentSpec(
            name,
            self._type,
            positional=args,
            varargs=varargs,
            kwargs=kws,
            kwonlyargs=kwo,
            defaults=self._get_defaults(args, defaults, kwo_defaults)
        )
        spec.types = self._get_types(handler, annotations, spec)
        return spec