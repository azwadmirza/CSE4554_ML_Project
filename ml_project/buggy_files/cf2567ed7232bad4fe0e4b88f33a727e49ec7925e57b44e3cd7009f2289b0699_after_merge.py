def display_as_type(v: AnyType) -> str:
    if not isinstance(v, typing_base) and not isinstance(v, type):
        v = type(v)

    if isinstance(v, type) and issubclass(v, Enum):
        if issubclass(v, int):
            return 'int'
        elif issubclass(v, str):
            return 'str'
        else:
            return 'enum'

    try:
        return v.__name__
    except AttributeError:
        # happens with unions
        return str(v)