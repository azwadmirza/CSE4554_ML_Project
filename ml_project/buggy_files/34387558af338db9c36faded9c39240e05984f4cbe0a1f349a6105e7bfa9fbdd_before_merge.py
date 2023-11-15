def convert_field_to_int(field, registry=None):
    return Int(description=field.help_text, required=not field.null)