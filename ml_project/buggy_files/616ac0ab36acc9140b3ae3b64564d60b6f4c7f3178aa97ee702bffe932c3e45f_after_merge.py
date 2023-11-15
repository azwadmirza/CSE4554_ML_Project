def convert_field_to_float(field, registry=None):
    return Float(
        description=get_django_field_description(field), required=not field.null
    )