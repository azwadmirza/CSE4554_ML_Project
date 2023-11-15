def get_field_info_schema(field: ModelField) -> Tuple[Dict[str, Any], bool]:
    schema_overrides = False

    # If no title is explicitly set, we don't set title in the schema for enums.
    # The behaviour is the same as `BaseModel` reference, where the default title
    # is in the definitions part of the schema.
    schema: Dict[str, Any] = {}
    if field.field_info.title or not lenient_issubclass(field.type_, Enum):
        schema['title'] = field.field_info.title or field.alias.title().replace('_', ' ')

    if field.field_info.title:
        schema_overrides = True

    if field.field_info.description:
        schema['description'] = field.field_info.description
        schema_overrides = True

    if (
        not field.required
        and not field.field_info.const
        and field.default is not None
        and not is_callable_type(field.outer_type_)
    ):
        schema['default'] = encode_default(field.default)
        schema_overrides = True

    return schema, schema_overrides