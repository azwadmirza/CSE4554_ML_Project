def convert_django_field_with_choices(
    field, registry=None, convert_choices_to_enum=True
):
    if registry is not None:
        converted = registry.get_converted_field(field)
        if converted:
            return converted
    choices = getattr(field, "choices", None)
    if choices and convert_choices_to_enum:
        enum = convert_choice_field_to_enum(field)
        required = not (field.blank or field.null)
        converted = enum(
            description=get_django_field_description(field), required=required
        )
    else:
        converted = convert_django_field(field, registry)
    if registry is not None:
        registry.register_converted_field(field, converted)
    return converted