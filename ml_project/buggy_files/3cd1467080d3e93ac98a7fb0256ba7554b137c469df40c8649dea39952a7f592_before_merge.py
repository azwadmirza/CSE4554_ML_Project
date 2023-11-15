def add_field_type_to_schema(field_type: Any, schema: Dict[str, Any]) -> None:
    """
    Update the given `schema` with the type-specific metadata for the given `field_type`.

    This function looks through `field_class_to_schema` for a class that matches the given `field_type`,
    and then modifies the given `schema` with the information from that type.
    """
    for type_, t_schema in field_class_to_schema:
        if issubclass(field_type, type_):
            schema.update(t_schema)
            break