    def dec(f):
        # avoid validators with duplicated names since without this validators can be overwritten silently
        # which generally isn't the intended behaviour, don't run in ipython - see #312
        if not in_ipython():  # pragma: no branch
            ref = f.__module__ + '.' + f.__qualname__
            if ref in _FUNCS:
                raise ConfigError(f'duplicate validator function "{ref}"')
            _FUNCS.add(ref)
        f_cls = classmethod(f)
        f_cls.__validator_config = fields, Validator(f, pre, whole, always, check_fields)
        return f_cls