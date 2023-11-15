def print_extends(type_):
    strawberry_type = get_strawberry_type_for_graphql_type(type_)

    if strawberry_type and getattr(strawberry_type, "_federation_extend", False):
        return "extend "

    return ""