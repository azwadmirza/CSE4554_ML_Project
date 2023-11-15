def convert_field_to_boolean(field, registry=None):
    return Boolean(
        description=get_django_field_description(field), required=not field.null
    )