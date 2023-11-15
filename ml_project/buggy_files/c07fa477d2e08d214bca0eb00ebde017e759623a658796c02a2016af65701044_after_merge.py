def convert_form_field_to_string_list(field):
    return List(
        String, description=get_form_field_description(field), required=field.required
    )