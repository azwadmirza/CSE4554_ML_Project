def convert_form_field_to_boolean(field):
    return Boolean(description=field.help_text, required=field.required)