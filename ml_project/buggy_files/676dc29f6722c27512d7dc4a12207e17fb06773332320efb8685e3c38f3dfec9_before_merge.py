def entities_resolver(root, info, representations):
    results = []

    for representation in representations:
        type_name = representation.pop("__typename")
        graphql_type = info.schema.get_type(type_name)

        result = get_strawberry_type_for_graphql_type(graphql_type).resolve_reference(
            **representation
        )
        results.append(result)

    return results