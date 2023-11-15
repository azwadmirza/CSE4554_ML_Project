def type(
    cls: Type = None,
    *,
    name: str = None,
    description: str = None,
    keys: List[str] = None,
    extend: bool = False
):
    return base_type(
        cls,
        name=name,
        description=description,
        federation=FederationTypeParams(keys=keys or [], extend=extend),
    )