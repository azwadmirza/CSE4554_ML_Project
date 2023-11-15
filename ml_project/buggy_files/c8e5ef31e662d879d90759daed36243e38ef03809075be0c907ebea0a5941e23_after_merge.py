def ensure_schema_type_expr_type(
    schema: s_schema.Schema,
    type_shell: TypeExprShell,
    parent_cmd: sd.Command,
    *,
    src_context: typing.Optional[parsing.ParserContext] = None,
    context: sd.CommandContext,
) -> Optional[sd.Command]:

    name = type_shell.get_name(schema)
    texpr_type = schema.get(name, default=None, type=Type)
    cmd = None
    if texpr_type is None:
        cmd = type_shell.as_create_delta(schema)
        if cmd is not None:
            parent_cmd.add_prerequisite(cmd)

    return cmd