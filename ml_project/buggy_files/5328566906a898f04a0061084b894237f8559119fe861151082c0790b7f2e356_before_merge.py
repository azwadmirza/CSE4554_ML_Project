def convert_field_to_boolean(field, registry=None):
    return Boolean(description=field.help_text, required=not field.null)