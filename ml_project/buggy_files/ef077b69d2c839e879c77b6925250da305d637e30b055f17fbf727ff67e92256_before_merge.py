def convert_form_field_to_int(field):
    return Int(description=field.help_text, required=field.required)