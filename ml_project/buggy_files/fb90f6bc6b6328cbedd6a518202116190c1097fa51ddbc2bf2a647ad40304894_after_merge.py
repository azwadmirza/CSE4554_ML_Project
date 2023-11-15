def _process_type(
    cls,
    *,
    name: Optional[str] = None,
    is_input: bool = False,
    is_interface: bool = False,
    description: Optional[str] = None,
    federation: Optional[FederationTypeParams] = None
):
    name = name or to_camel_case(cls.__name__)

    wrapped = dataclasses.dataclass(cls)

    interfaces = _get_interfaces(wrapped)

    wrapped._type_definition = TypeDefinition(
        name=name,
        is_input=is_input,
        is_interface=is_interface,
        is_generic=is_generic(cls),
        interfaces=interfaces,
        description=description,
        federation=federation or FederationTypeParams(),
        origin=cls,
    )

    return wrapped