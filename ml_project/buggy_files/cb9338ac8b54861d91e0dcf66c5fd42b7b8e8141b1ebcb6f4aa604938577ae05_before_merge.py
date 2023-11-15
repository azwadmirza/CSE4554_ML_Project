def analyze_class_attribute_access(itype: Instance,
                                   name: str,
                                   context: Context,
                                   is_lvalue: bool,
                                   builtin_type: Callable[[str], Instance],
                                   not_ready_callback: Callable[[str, Context], None],
                                   msg: MessageBuilder) -> Type:
    node = itype.type.get(name)
    if not node:
        if itype.type.fallback_to_any:
            return AnyType()
        return None

    is_decorated = isinstance(node.node, Decorator)
    is_method = is_decorated or isinstance(node.node, FuncDef)
    if is_lvalue:
        if is_method:
            msg.cant_assign_to_method(context)
        if isinstance(node.node, TypeInfo):
            msg.fail(messages.CANNOT_ASSIGN_TO_TYPE, context)

    if itype.type.is_enum and not (is_lvalue or is_decorated or is_method):
        return itype

    t = node.type
    if t:
        if isinstance(t, PartialType):
            return handle_partial_attribute_type(t, is_lvalue, msg, node.node)
        is_classmethod = is_decorated and cast(Decorator, node.node).func.is_class
        return add_class_tvars(t, itype.type, is_classmethod, builtin_type)
    elif isinstance(node.node, Var):
        not_ready_callback(name, context)
        return AnyType()

    if isinstance(node.node, TypeInfo):
        return type_object_type(node.node, builtin_type)

    if is_decorated:
        # TODO: Return type of decorated function. This is quick hack to work around #998.
        return AnyType()
    else:
        return function_type(cast(FuncBase, node.node), builtin_type('builtins.function'))