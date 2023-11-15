    def __call__(self, f):
        f._field_definition = self._field_definition
        f._field_definition.name = f._field_definition.name or to_camel_case(f.__name__)
        f._field_definition.base_resolver = f
        f._field_definition.origin = f
        f._field_definition.arguments = get_arguments_from_resolver(
            f, f._field_definition.name
        )

        check_return_annotation(f._field_definition)

        f._field_definition.type = f.__annotations__["return"]

        return f