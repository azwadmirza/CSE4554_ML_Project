def has_type_var(annotation) -> bool:
    """
    Returns True if the annotation or any of
    its argument have a TypeVar as argument.
    """
    return any(
        is_type_var(arg) or has_type_var(arg)
        for arg in getattr(annotation, "__args__", [])
    )