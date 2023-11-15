def is_union(annotation: Type) -> bool:
    """Returns True if annotation is a Union"""

    annotation_origin = getattr(annotation, "__origin__", None)

    return annotation_origin == typing.Union