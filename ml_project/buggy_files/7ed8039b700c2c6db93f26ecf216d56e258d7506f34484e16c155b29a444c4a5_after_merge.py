def convert_form_field_to_date(field):
    return Date(description=get_form_field_description(field), required=field.required)