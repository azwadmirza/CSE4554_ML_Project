def get_optional_annotation(annotation: Type) -> Type:
    types = annotation.__args__
    non_none_types = [x for x in types if x != None.__class__]  # noqa:E711

    return non_none_types[0]