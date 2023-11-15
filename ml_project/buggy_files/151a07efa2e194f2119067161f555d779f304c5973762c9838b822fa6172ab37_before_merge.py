def _get_resolver(cls, field_name):
    class_field = getattr(cls, field_name, None)

    if class_field and getattr(class_field, "resolver", None):
        return class_field.resolver

    def _resolver(root, info):
        if not root:
            return None

        field_resolver = getattr(root, field_name, None)

        if getattr(field_resolver, IS_STRAWBERRY_FIELD, False):
            return field_resolver(root, info)

        elif field_resolver.__class__ is strawberry_field:
            # TODO: support default values
            return None

        return field_resolver

    return _resolver