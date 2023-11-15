def _process_enum(cls, name=None, description=None):
    if not isinstance(cls, EnumMeta):
        raise NotAnEnum()

    if not name:
        name = cls.__name__

    description = description

    cls._enum_definition = EnumDefinition(
        name=name,
        values=[EnumValue(item.name, item.value) for item in cls],
        description=description,
    )

    return cls