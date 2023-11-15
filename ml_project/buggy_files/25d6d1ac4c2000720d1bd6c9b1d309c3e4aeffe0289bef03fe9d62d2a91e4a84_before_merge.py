def convert_field_to_uuid(field, registry=None):
    return UUID(description=field.help_text, required=not field.null)