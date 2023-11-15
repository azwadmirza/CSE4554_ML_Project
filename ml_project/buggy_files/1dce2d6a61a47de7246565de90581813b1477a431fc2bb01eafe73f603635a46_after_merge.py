def analyze_class_attribute_access(itype: Instance,
                                   name: str,
                                   mx: MemberContext) -> Optional[Type]:
    """original_type is the type of E in the expression E.var"""
    node = itype.type.get(name)
    if not node:
        if itype.type.fallback_to_any:
            return AnyType(TypeOfAny.special_form)
        return None

    is_decorated = isinstance(node.node, Decorator)
    is_method = is_decorated or isinstance(node.node, FuncBase)
    if mx.is_lvalue:
        if is_method:
            mx.msg.cant_assign_to_method(mx.context)
        if isinstance(node.node, TypeInfo):
            mx.msg.fail(message_registry.CANNOT_ASSIGN_TO_TYPE, mx.context)

    # If a final attribute was declared on `self` in `__init__`, then it
    # can't be accessed on the class object.
    if node.implicit and isinstance(node.node, Var) and node.node.is_final:
        mx.msg.fail(message_registry.CANNOT_ACCESS_FINAL_INSTANCE_ATTR
                    .format(node.node.name()), mx.context)

    # An assignment to final attribute on class object is also always an error,
    # independently of types.
    if mx.is_lvalue and not mx.chk.get_final_context():
        check_final_member(name, itype.type, mx.msg, mx.context)

    if itype.type.is_enum and not (mx.is_lvalue or is_decorated or is_method):
        return itype

    t = node.type
    if t:
        if isinstance(t, PartialType):
            symnode = node.node
            assert isinstance(symnode, Var)
            return mx.chk.handle_partial_var_type(t, mx.is_lvalue, symnode, mx.context)

        # Find the class where method/variable was defined.
        # mypyc hack to workaround mypy misunderstanding multiple inheritance (#3603)
        node_node = node.node  # type: Any
        if isinstance(node_node, Decorator):
            super_info = node_node.var.info  # type: Optional[TypeInfo]
        elif isinstance(node_node, (Var, FuncBase)):
            super_info = node_node.info
        else:
            super_info = None

        # Map the type to how it would look as a defining class. For example:
        #     class C(Generic[T]): ...
        #     class D(C[Tuple[T, S]]): ...
        #     D[int, str].method()
        # Here itype is D[int, str], isuper is C[Tuple[int, str]].
        if not super_info:
            isuper = None
        else:
            isuper = map_instance_to_supertype(itype, super_info)

        if isinstance(node.node, Var):
            assert isuper is not None
            # Check if original variable type has type variables. For example:
            #     class C(Generic[T]):
            #         x: T
            #     C.x  # Error, ambiguous access
            #     C[int].x  # Also an error, since C[int] is same as C at runtime
            if isinstance(t, TypeVarType) or get_type_vars(t):
                # Exception: access on Type[...], including first argument of class methods is OK.
                if not isinstance(mx.original_type, TypeType):
                    mx.msg.fail(message_registry.GENERIC_INSTANCE_VAR_CLASS_ACCESS, mx.context)

            # Erase non-mapped variables, but keep mapped ones, even if there is an error.
            # In the above example this means that we infer following types:
            #     C.x -> Any
            #     C[int].x -> int
            t = erase_typevars(expand_type_by_instance(t, isuper))

        is_classmethod = ((is_decorated and cast(Decorator, node.node).func.is_class)
                          or (isinstance(node.node, FuncBase) and node.node.is_class))
        result = add_class_tvars(t, itype, isuper, is_classmethod, mx.builtin_type,
                                 mx.original_type)
        if not mx.is_lvalue:
            result = analyze_descriptor_access(mx.original_type, result, mx.builtin_type,
                                               mx.msg, mx.context, chk=mx.chk)
        return result
    elif isinstance(node.node, Var):
        mx.not_ready_callback(name, mx.context)
        return AnyType(TypeOfAny.special_form)

    if isinstance(node.node, TypeVarExpr):
        mx.msg.fail(message_registry.CANNOT_USE_TYPEVAR_AS_EXPRESSION.format(
                    itype.type.name(), name), mx.context)
        return AnyType(TypeOfAny.from_error)

    if isinstance(node.node, TypeInfo):
        return type_object_type(node.node, mx.builtin_type)

    if isinstance(node.node, MypyFile):
        # Reference to a module object.
        return mx.builtin_type('types.ModuleType')

    if isinstance(node.node, TypeAlias) and isinstance(node.node.target, Instance):
        return instance_alias_type(node.node, mx.builtin_type)

    if is_decorated:
        assert isinstance(node.node, Decorator)
        if node.node.type:
            return node.node.type
        else:
            mx.not_ready_callback(name, mx.context)
            return AnyType(TypeOfAny.from_error)
    else:
        return function_type(cast(FuncBase, node.node), mx.builtin_type('builtins.function'))