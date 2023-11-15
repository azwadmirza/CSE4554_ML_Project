def is_type_var(annotation) -> bool:
    """Returns True if the annotation is a TypeVar."""

    return isinstance(annotation, typing.TypeVar)  # type:ignore