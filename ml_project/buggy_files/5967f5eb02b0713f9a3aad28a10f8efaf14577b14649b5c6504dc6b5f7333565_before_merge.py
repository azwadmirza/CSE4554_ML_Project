def __enum_validate__(validator, enums, instance, schema):
    if instance not in enums:
        yield jsonschema.exceptions.ValidationError(
            _("'%s' is not one of ['%s']") % (instance, "', '".join(enums))
        )