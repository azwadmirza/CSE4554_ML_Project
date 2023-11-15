def convert_postgres_field_to_string(field, registry=None):
    return JSONString(
        description=get_django_field_description(field), required=not field.null
    )