def convert_field_to_id(field, registry=None):
    return ID(description=get_django_field_description(field), required=not field.null)