def convert_form_field_to_datetime(field):
    return DateTime(description=field.help_text, required=field.required)