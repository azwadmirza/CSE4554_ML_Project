def convert_field_to_string(field, registry=None):
    return String(description=field.help_text, required=not field.null)