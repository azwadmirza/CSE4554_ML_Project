def convert_field_to_uuid(field, registry=None):
    return UUID(
        description=get_django_field_description(field), required=not field.null
    )