def convert_form_field_to_uuid(field):
    return UUID(description=field.help_text, required=field.required)