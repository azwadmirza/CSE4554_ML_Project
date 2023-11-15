def convert_datetime_to_string(field, registry=None):
    return DateTime(description=field.help_text, required=not field.null)