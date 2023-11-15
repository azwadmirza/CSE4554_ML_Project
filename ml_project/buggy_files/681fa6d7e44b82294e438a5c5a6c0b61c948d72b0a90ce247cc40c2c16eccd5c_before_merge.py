def enum_validator(v: Any, field: 'Field', config: 'BaseConfig') -> Enum:
    try:
        enum_v = field.type_(v)
    except ValueError:
        raise errors.EnumError(enum_type=field.type_)
    return enum_v.value if config.use_enum_values else enum_v