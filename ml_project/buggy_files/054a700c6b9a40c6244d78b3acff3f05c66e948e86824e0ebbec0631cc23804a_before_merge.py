def convert_form_field_to_string(field):
    return String(description=field.help_text, required=field.required)