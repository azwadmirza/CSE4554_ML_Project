def ensure_schema_type_expr_type(
    schema: s_schema.Schema,
    type_shell: TypeExprShell,
    parent_cmd: sd.Command,
    *,
    src_context: typing.Optional[parsing.ParserContext] = None,
    context: sd.CommandContext,
) -> Optional[sd.Command]:

    module = type_shell.module
    components = type_shell.components

    if isinstance(type_shell, UnionTypeShell):
        type_id, type_name = get_union_type_id(
            schema,
            components,
            opaque=type_shell.opaque,
            module=module,
        )
    elif isinstance(type_shell, IntersectionTypeShell):
        type_id, type_name = get_intersection_type_id(
            schema,
            components,
            module=module,
        )
    else:
        raise AssertionError(f'unexpected type shell: {type_shell!r}')

    texpr_type = schema.get_by_id(type_id, None, type=Type)

    cmd = None
    if texpr_type is None:
        cmd = type_shell.as_create_delta(schema)
        if cmd is not None:
            parent_cmd.add_prerequisite(cmd)

    return cmd