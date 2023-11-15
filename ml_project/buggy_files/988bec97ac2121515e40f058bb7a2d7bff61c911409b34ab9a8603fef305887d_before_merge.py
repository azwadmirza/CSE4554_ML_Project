def print_fields(type_) -> str:
    strawberry_type = get_strawberry_type_for_graphql_type(type_)
    strawberry_fields = dataclasses.fields(strawberry_type) if strawberry_type else []

    def _get_metadata(field_name):
        return next(
            (
                f.metadata
                for f in strawberry_fields
                if (getattr(f, "field_name", None) or f.name) == field_name
            ),
            None,
        )

    fields = [
        print_description(field, "  ", not i)
        + f"  {name}"
        + print_args(field.args, "  ")
        + f": {field.type}"
        + print_federation_field_directive(field, _get_metadata(name))
        + print_deprecated(field)
        for i, (name, field) in enumerate(type_.fields.items())
    ]
    return print_block(fields)