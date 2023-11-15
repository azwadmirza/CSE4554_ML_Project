def is_type_var(annotation: Type) -> bool:
    """Returns True if the annotation is a TypeVar."""

    return isinstance(annotation, TypeVar)  # type:ignore