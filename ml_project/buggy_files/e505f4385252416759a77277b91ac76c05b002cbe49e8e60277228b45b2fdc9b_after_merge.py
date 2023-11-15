def convert_form_field_to_uuid(field):
    return UUID(description=get_form_field_description(field), required=field.required)