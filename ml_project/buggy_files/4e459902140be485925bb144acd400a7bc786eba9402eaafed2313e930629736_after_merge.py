def convert_postgres_range_to_string(field, registry=None):
    inner_type = convert_django_field(field.base_field)
    if not isinstance(inner_type, (List, NonNull)):
        inner_type = type(inner_type)
    return List(
        inner_type,
        description=get_django_field_description(field),
        required=not field.null,
    )