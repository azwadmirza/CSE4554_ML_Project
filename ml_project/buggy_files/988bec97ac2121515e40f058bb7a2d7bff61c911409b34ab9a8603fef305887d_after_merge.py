def print_fields(type_, schema: BaseSchema) -> str:
    strawberry_type = cast(TypeDefinition, schema.get_type_by_name(type_.name))

    fields = []

    for i, (name, field) in enumerate(type_.fields.items()):
        field_definition = strawberry_type.get_field(name) if strawberry_type else None

        fields.append(
            print_description(field, "  ", not i)
            + f"  {name}"
            + print_args(field.args, "  ")
            + f": {field.type}"
            + print_federation_field_directive(field_definition)
            + print_deprecated(field)
        )

    return print_block(fields)