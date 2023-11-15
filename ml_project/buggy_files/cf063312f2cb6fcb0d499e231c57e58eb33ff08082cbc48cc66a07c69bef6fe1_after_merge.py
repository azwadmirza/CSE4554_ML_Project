def convert_form_field_to_boolean(field):
    return Boolean(
        description=get_form_field_description(field), required=field.required
    )