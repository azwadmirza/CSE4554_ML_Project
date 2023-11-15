def convert_form_field_to_float(field):
    return Float(description=get_form_field_description(field), required=field.required)