def convert_datetime_to_string(field, registry=None):
    return DateTime(
        description=get_django_field_description(field), required=not field.null
    )