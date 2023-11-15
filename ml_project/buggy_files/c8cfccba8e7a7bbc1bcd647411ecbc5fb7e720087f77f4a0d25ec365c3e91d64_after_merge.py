def _process_scalar(
    cls,
    *,
    name: str,
    description: str,
    serialize: Callable,
    parse_value: Callable,
    parse_literal: Callable
):

    name = name or to_camel_case(cls.__name__)

    wrapper = ScalarWrapper(cls)
    wrapper._scalar_definition = ScalarDefinition(
        name=name,
        description=description,
        serialize=serialize,
        parse_literal=parse_literal,
        parse_value=parse_value,
    )

    SCALAR_REGISTRY[cls] = wrapper._scalar_definition

    return wrapper