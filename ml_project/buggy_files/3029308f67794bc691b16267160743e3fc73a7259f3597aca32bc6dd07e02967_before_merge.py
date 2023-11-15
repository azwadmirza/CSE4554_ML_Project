def convert_field_to_id(field, registry=None):
    return ID(description=field.help_text, required=not field.null)