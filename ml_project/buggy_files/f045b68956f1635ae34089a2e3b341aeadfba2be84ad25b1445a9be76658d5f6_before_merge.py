def _process_enum(cls, name=None, description=None):
    if not isinstance(cls, EnumMeta):
        raise NotAnEnum()

    if not name:
        name = cls.__name__

    description = description or cls.__doc__

    graphql_type = GraphQLEnumType(
        name=name,
        values=[(item.name, GraphQLEnumValue(item.value)) for item in cls],
        description=description,
    )

    register_type(cls, graphql_type)

    return cls