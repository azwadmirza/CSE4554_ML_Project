def convert_time_to_string(field, registry=None):
    return Time(
        description=get_django_field_description(field), required=not field.null
    )