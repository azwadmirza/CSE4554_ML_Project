def _process_scalar(cls, *, name, description, serialize, parse_value, parse_literal):
    if name is None:
        name = cls.__name__

    graphql_type = GraphQLScalarType(
        name=name,
        description=description,
        serialize=serialize,
        parse_value=parse_value,
        parse_literal=parse_literal,
    )

    register_type(cls, graphql_type, store_type_information=False)

    return cls