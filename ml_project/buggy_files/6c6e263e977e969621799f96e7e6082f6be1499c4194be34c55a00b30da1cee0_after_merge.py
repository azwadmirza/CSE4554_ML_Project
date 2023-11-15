def get_list_annotation(annotation: Type) -> Type:
    return annotation.__args__[0]