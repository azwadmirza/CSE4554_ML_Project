def convert_time_to_string(field, registry=None):
    return Time(description=field.help_text, required=not field.null)