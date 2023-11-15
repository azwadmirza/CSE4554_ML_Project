def print_federation_key_directive(type_):
    strawberry_type = get_strawberry_type_for_graphql_type(type_)

    if not strawberry_type:
        return ""

    keys = getattr(strawberry_type, "_federation_keys", [])

    parts = []

    for key in keys:
        parts.append(f'@key(fields: "{key}")')

    if not parts:
        return ""

    return " " + " ".join(parts)