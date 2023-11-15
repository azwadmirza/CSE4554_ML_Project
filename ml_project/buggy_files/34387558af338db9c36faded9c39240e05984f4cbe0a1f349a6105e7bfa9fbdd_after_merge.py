def convert_field_to_int(field, registry=None):
    return Int(description=get_django_field_description(field), required=not field.null)