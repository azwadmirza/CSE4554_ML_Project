def is_list(annotation):
    """Returns True if annotation is a typing.List"""

    annotation_origin = getattr(annotation, "__origin__", None)

    return annotation_origin == list