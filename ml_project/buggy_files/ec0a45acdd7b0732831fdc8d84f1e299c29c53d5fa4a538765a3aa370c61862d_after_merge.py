def convert_form_field_to_time(field):
    return Time(description=get_form_field_description(field), required=field.required)