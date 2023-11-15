def analyze_var(name: str,
                var: Var,
                itype: Instance,
                info: TypeInfo,
                mx: MemberContext, *,
                implicit: bool = False) -> Type:
    """Analyze access to an attribute via a Var node.

    This is conceptually part of analyze_member_access and the arguments are similar.

    itype is the class object in which var is defined
    original_type is the type of E in the expression E.var
    if implicit is True, the original Var was created as an assignment to self
    """
    # Found a member variable.
    itype = map_instance_to_supertype(itype, var.info)
    typ = var.type
    if typ:
        if isinstance(typ, PartialType):
            return mx.chk.handle_partial_var_type(typ, mx.is_lvalue, var, mx.context)
        if mx.is_lvalue and var.is_property and not var.is_settable_property:
            # TODO allow setting attributes in subclass (although it is probably an error)
            mx.msg.read_only_property(name, itype.type, mx.context)
        if mx.is_lvalue and var.is_classvar:
            mx.msg.cant_assign_to_classvar(name, mx.context)
        t = get_proper_type(expand_type_by_instance(typ, itype))
        result = t  # type: Type
        typ = get_proper_type(typ)
        if var.is_initialized_in_class and isinstance(typ, FunctionLike) and not typ.is_type_obj():
            if mx.is_lvalue:
                if var.is_property:
                    if not var.is_settable_property:
                        mx.msg.read_only_property(name, itype.type, mx.context)
                else:
                    mx.msg.cant_assign_to_method(mx.context)

            if not var.is_staticmethod:
                # Class-level function objects and classmethods become bound methods:
                # the former to the instance, the latter to the class.
                functype = typ
                # Use meet to narrow original_type to the dispatched type.
                # For example, assume
                # * A.f: Callable[[A1], None] where A1 <: A (maybe A1 == A)
                # * B.f: Callable[[B1], None] where B1 <: B (maybe B1 == B)
                # * x: Union[A1, B1]
                # In `x.f`, when checking `x` against A1 we assume x is compatible with A
                # and similarly for B1 when checking agains B
                dispatched_type = meet.meet_types(mx.original_type, itype)
                signature = freshen_function_type_vars(functype)
                signature = check_self_arg(signature, dispatched_type, var.is_classmethod,
                                          mx.context, name, mx.msg)
                signature = bind_self(signature, mx.self_type, var.is_classmethod)
                expanded_signature = get_proper_type(expand_type_by_instance(signature, itype))
                if var.is_property:
                    # A property cannot have an overloaded type => the cast is fine.
                    assert isinstance(expanded_signature, CallableType)
                    result = expanded_signature.ret_type
                else:
                    result = expanded_signature
    else:
        if not var.is_ready:
            mx.not_ready_callback(var.name, mx.context)
        # Implicit 'Any' type.
        result = AnyType(TypeOfAny.special_form)
    fullname = '{}.{}'.format(var.info.fullname, name)
    hook = mx.chk.plugin.get_attribute_hook(fullname)
    if result and not mx.is_lvalue and not implicit:
        result = analyze_descriptor_access(mx.original_type, result, mx.builtin_type,
                                           mx.msg, mx.context, chk=mx.chk)
    if hook:
        result = hook(AttributeContext(get_proper_type(mx.original_type),
                                       result, mx.context, mx.chk))
    return result