def get_or_create_intersection_type(
    schema: s_schema.Schema,
    components: Iterable[ObjectType],
    *,
    module: Optional[str] = None,
) -> Tuple[s_schema.Schema, ObjectType, bool]:

    name = s_types.get_intersection_type_name(
        (c.get_name(schema) for c in components),
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
                intersection_of=so.ObjectSet.create(schema, components),
                abstract=True,
                final=True,
            ),
        )

        ptrs_dict = collections.defaultdict(list)

        for component in components:
            for pn, ptr in component.get_pointers(schema).items(schema):
                ptrs_dict[pn].append(ptr)

        intersection_pointers = {}

        for pn, ptrs in ptrs_dict.items():
            if len(ptrs) > 1:
                # The pointer is present in more than one component.
                schema, ptr = pointers.get_or_create_intersection_pointer(
                    schema,
                    ptrname=pn,
                    source=objtype,
                    components=set(ptrs),
                )
            else:
                ptr = ptrs[0]

            intersection_pointers[pn] = ptr

        for pn, ptr in intersection_pointers.items():
            if objtype.getptr(schema, pn) is None:
                schema = objtype.add_pointer(schema, ptr)

    assert isinstance(objtype, ObjectType)
    return schema, objtype, created