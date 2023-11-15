def validator(*fields, pre: bool = False, whole: bool = False, always: bool = False, check_fields: bool = True):
    """
    Decorate methods on the class indicating that they should be used to validate fields
    :param fields: which field(s) the method should be called on
    :param pre: whether or not this validator should be called before the standard validators (else after)
    :param whole: for complex objects (sets, lists etc.) whether to validate individual elements or the whole object
    :param always: whether this method and other validators should be called even if the value is missing
    :param check_fields: whether to check that the fields actually exist on the model
    """
    if not fields:
        raise ConfigError('validator with no fields specified')
    elif isinstance(fields[0], FunctionType):
        raise ConfigError(
            "validators should be used with fields and keyword arguments, not bare. "
            "E.g. usage should be `@validator('<field_name>', ...)`"
        )

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

    return dec