def convert_field_to_string(field, registry=None):
    return String(
        description=get_django_field_description(field), required=not field.null
    )