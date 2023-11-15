def convert_postgres_field_to_string(field, registry=None):
    return JSONString(description=field.help_text, required=not field.null)