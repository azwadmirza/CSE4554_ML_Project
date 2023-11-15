def convert_form_field_to_float(field):
    return Float(description=field.help_text, required=field.required)