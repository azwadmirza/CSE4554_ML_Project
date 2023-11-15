def convert_field_to_djangomodel(field, registry=None):
    model = field.related_model

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        return Field(
            _type,
            description=get_django_field_description(field),
            required=not field.null,
        )

    return Dynamic(dynamic_type)