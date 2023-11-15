def copy_method_to_another_class(
    ctx: ClassDefContext, self_type: Instance, new_method_name: str, method_node: FuncDef
) -> None:
    semanal_api = get_semanal_api(ctx)
    if method_node.type is None:
        if not semanal_api.final_iteration:
            semanal_api.defer()
            return

        arguments, return_type = build_unannotated_method_args(method_node)
        add_method(ctx, new_method_name, args=arguments, return_type=return_type, self_type=self_type)
        return

    method_type = method_node.type
    if not isinstance(method_type, CallableType):
        if not semanal_api.final_iteration:
            semanal_api.defer()
        return

    arguments = []
    bound_return_type = semanal_api.anal_type(method_type.ret_type, allow_placeholder=True)

    assert bound_return_type is not None

    if isinstance(bound_return_type, PlaceholderNode):
        return

    try:
        original_arguments = method_node.arguments[1:]
    except AttributeError:
        original_arguments = []

    for arg_name, arg_type, original_argument in zip(
        method_type.arg_names[1:], method_type.arg_types[1:], original_arguments
    ):
        bound_arg_type = semanal_api.anal_type(arg_type, allow_placeholder=True)
        if bound_arg_type is None and not semanal_api.final_iteration:
            semanal_api.defer()
            return

        assert bound_arg_type is not None

        if isinstance(bound_arg_type, PlaceholderNode):
            return

        var = Var(name=original_argument.variable.name, type=arg_type)
        var.line = original_argument.variable.line
        var.column = original_argument.variable.column
        argument = Argument(
            variable=var,
            type_annotation=bound_arg_type,
            initializer=original_argument.initializer,
            kind=original_argument.kind,
        )
        argument.set_line(original_argument)
        arguments.append(argument)

    add_method(ctx, new_method_name, args=arguments, return_type=bound_return_type, self_type=self_type)