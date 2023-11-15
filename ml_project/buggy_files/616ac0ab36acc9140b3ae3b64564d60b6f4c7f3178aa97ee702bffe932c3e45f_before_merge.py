def convert_field_to_float(field, registry=None):
    return Float(description=field.help_text, required=not field.null)