def convert_form_field_to_nullboolean(field):
    return Boolean(description=get_form_field_description(field))