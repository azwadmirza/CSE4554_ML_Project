def analyze_class_attribute_access(itype: Instance,
                                   name: str,
                                   context: Context,
                                   is_lvalue: bool,
                                   builtin_type: Callable[[str], Instance],
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
        is_classmethod = is_decorated and cast(Decorator, node.node).func.is_class
        return add_class_tvars(t, itype.type, is_classmethod, builtin_type)
    elif isinstance(node.node, Var):
        msg.cannot_determine_type(name, context)
        return AnyType()

    if isinstance(node.node, TypeInfo):
        return type_object_type(cast(TypeInfo, node.node), builtin_type)

    return function_type(cast(FuncBase, node.node), builtin_type('builtins.function'))