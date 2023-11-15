def get_or_create_union_type(
    schema: s_schema.Schema,
    components: Iterable[ObjectType],
    *,
    opaque: bool = False,
    module: Optional[str] = None,
) -> Tuple[s_schema.Schema, ObjectType, bool]:

    name = s_types.get_union_type_name(
        (c.get_name(schema) for c in components),
        opaque=opaque,
        module=module,
    )

    objtype = schema.get(name, default=None, type=ObjectType)
    created = objtype is None
    if objtype is None:
        components = list(components)

        std_object = schema.get('std::BaseObject', type=ObjectType)

        schema, objtype = std_object.derive_subtype(
            schema,
            name=name,
            attrs=dict(
                union_of=so.ObjectSet.create(schema, components),
                is_opaque_union=opaque,
                abstract=True,
                final=True,
            ),
        )

        if not opaque:

            schema = sources.populate_pointer_set_for_source_union(
                schema,
                cast(List[sources.Source], components),
                objtype,
                modname=module,
            )

    return schema, objtype, created