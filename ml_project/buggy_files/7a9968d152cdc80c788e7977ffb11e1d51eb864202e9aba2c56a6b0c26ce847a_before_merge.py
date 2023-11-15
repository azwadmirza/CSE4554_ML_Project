    def dec(f):
        ref = f.__module__ + '.' + f.__qualname__
        if ref in _FUNCS:
            raise ConfigError(f'duplicate validator function "{ref}"')
        _FUNCS.add(ref)
        f_cls = classmethod(f)
        f_cls.__validator_config = fields, Validator(f, pre, whole, always, check_fields)
        return f_cls