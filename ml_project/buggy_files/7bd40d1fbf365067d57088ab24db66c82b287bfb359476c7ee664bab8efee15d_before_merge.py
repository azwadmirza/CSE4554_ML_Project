def convert_date_to_string(field, registry=None):
    return Date(description=field.help_text, required=not field.null)