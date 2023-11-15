def convert_form_field_to_int(field):
    return Int(description=get_form_field_description(field), required=field.required)