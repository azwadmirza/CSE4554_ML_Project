def convert_form_field_to_date(field):
    return Date(description=field.help_text, required=field.required)