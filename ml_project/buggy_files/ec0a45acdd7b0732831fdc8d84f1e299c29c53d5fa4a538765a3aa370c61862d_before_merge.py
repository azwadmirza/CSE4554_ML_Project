def convert_form_field_to_time(field):
    return Time(description=field.help_text, required=field.required)