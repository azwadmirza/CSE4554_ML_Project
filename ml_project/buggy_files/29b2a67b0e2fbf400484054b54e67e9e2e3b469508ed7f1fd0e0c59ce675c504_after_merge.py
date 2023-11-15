def is_generic(annotation: Type) -> bool:
    """Returns True if the annotation is or extends a generic."""
    return (
        isinstance(annotation, type)
        and issubclass(annotation, typing.Generic)  # type:ignore
        or isinstance(annotation, typing._GenericAlias)  # type:ignore
        and annotation.__origin__
        not in (list, typing.Union, tuple, typing.ClassVar, AsyncGenerator,)
    )