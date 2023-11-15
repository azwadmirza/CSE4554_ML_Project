def convert_form_field_to_string(field):
    return String(
        description=get_form_field_description(field), required=field.required
    )