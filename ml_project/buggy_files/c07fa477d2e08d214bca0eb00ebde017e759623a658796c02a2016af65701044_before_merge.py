def convert_form_field_to_string_list(field):
    return List(String, description=field.help_text, required=field.required)