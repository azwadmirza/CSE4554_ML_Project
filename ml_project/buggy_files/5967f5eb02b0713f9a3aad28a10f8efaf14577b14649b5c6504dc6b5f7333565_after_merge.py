def __enum_validate__(validator, enums, instance, schema):
    if instance not in enums:
        yield jsonschema.exceptions.ValidationError(
            _("'{value}' is not one of ['{allowed_values}']").format(
                value=instance, allowed_values="', '".join(enums))
        )