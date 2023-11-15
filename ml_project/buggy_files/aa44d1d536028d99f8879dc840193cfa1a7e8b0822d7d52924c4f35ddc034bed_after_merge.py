def convert_postgres_array_to_list(field, registry=None):
    base_type = convert_django_field(field.base_field)
    if not isinstance(base_type, (List, NonNull)):
        base_type = type(base_type)
    return List(
        base_type,
        description=get_django_field_description(field),
        required=not field.null,
    )