def convert_form_field_to_nullboolean(field):
    return Boolean(description=field.help_text)