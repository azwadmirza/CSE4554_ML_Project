def convert_form_field_to_datetime(field):
    return DateTime(
        description=get_form_field_description(field), required=field.required
    )