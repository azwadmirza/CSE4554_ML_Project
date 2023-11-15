def convert_date_to_string(field, registry=None):
    return Date(
        description=get_django_field_description(field), required=not field.null
    )