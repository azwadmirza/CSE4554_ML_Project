def enum_validator(v: Any, field: 'Field', config: 'BaseConfig') -> Enum:
    try:
        enum_v = field.type_(v)
    except ValueError:
        # field.type_ should be an enum, so will be iterable
        raise errors.EnumError(enum_values=list(field.type_))  # type: ignore
    return enum_v.value if config.use_enum_values else enum_v