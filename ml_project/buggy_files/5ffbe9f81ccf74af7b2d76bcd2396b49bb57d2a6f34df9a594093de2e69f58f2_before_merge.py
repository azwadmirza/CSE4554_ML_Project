def analyze_member_access(name: str,
                          typ: Type,
                          node: Context,
                          is_lvalue: bool,
                          is_super: bool,
                          is_operator: bool,
                          builtin_type: Callable[[str], Instance],
                          not_ready_callback: Callable[[str, Context], None],
                          msg: MessageBuilder, *,
                          original_type: Type,
                          chk: 'mypy.checker.TypeChecker',
                          override_info: Optional[TypeInfo] = None) -> Type:
    """Return the type of attribute `name` of typ.

    This is a general operation that supports various different variations:

      1. lvalue or non-lvalue access (i.e. setter or getter access)
      2. supertype access (when using super(); is_super == True and
         override_info should refer to the supertype)

    original_type is the most precise inferred or declared type of the base object
    that we have available. typ is generally a supertype of original_type.
    When looking for an attribute of typ, we may perform recursive calls targeting
    the fallback type, for example.
    original_type is always the type used in the initial call.
    """
    # TODO: this and following functions share some logic with subtypes.find_member,
    # consider refactoring.
    if isinstance(typ, Instance):
        if name == '__init__' and not is_super:
            # Accessing __init__ in statically typed code would compromise
            # type safety unless used via super().
            msg.fail(messages.CANNOT_ACCESS_INIT, node)
            return AnyType(TypeOfAny.from_error)

        # The base object has an instance type.

        info = typ.type
        if override_info:
            info = override_info

        if (experiments.find_occurrences and
                info.name() == experiments.find_occurrences[0] and
                name == experiments.find_occurrences[1]):
            msg.note("Occurrence of '{}.{}'".format(*experiments.find_occurrences), node)

        # Look up the member. First look up the method dictionary.
        method = info.get_method(name)
        if method:
            if method.is_property:
                assert isinstance(method, OverloadedFuncDef)
                first_item = cast(Decorator, method.items[0])
                return analyze_var(name, first_item.var, typ, info, node, is_lvalue, msg,
                                   original_type, not_ready_callback, chk=chk)
            if is_lvalue:
                msg.cant_assign_to_method(node)
            signature = function_type(method, builtin_type('builtins.function'))
            signature = freshen_function_type_vars(signature)
            if name == '__new__':
                # __new__ is special and behaves like a static method -- don't strip
                # the first argument.
                pass
            else:
                signature = bind_self(signature, original_type)
            typ = map_instance_to_supertype(typ, method.info)
            member_type = expand_type_by_instance(signature, typ)
            freeze_type_vars(member_type)
            return member_type
        else:
            # Not a method.
            return analyze_member_var_access(name, typ, info, node,
                                             is_lvalue, is_super, builtin_type,
                                             not_ready_callback, msg,
                                             original_type=original_type, chk=chk)
    elif isinstance(typ, AnyType):
        # The base object has dynamic type.
        return AnyType(TypeOfAny.from_another_any, source_any=typ)
    elif isinstance(typ, NoneTyp):
        if chk.should_suppress_optional_error([typ]):
            return AnyType(TypeOfAny.from_error)
        # The only attribute NoneType has are those it inherits from object
        return analyze_member_access(name, builtin_type('builtins.object'), node, is_lvalue,
                                     is_super, is_operator, builtin_type, not_ready_callback, msg,
                                     original_type=original_type, chk=chk)
    elif isinstance(typ, UnionType):
        # The base object has dynamic type.
        msg.disable_type_names += 1
        results = [analyze_member_access(name, subtype, node, is_lvalue, is_super,
                                         is_operator, builtin_type, not_ready_callback, msg,
                                         original_type=original_type, chk=chk)
                   for subtype in typ.relevant_items()]
        msg.disable_type_names -= 1
        return UnionType.make_simplified_union(results)
    elif isinstance(typ, TupleType):
        # Actually look up from the fallback instance type.
        return analyze_member_access(name, typ.fallback, node, is_lvalue, is_super,
                                     is_operator, builtin_type, not_ready_callback, msg,
                                     original_type=original_type, chk=chk)
    elif isinstance(typ, TypedDictType):
        # Actually look up from the fallback instance type.
        return analyze_member_access(name, typ.fallback, node, is_lvalue, is_super,
                                     is_operator, builtin_type, not_ready_callback, msg,
                                     original_type=original_type, chk=chk)
    elif isinstance(typ, FunctionLike) and typ.is_type_obj():
        # Class attribute.
        # TODO super?
        ret_type = typ.items()[0].ret_type
        if isinstance(ret_type, TupleType):
            ret_type = ret_type.fallback
        if isinstance(ret_type, Instance):
            if not is_operator:
                # When Python sees an operator (eg `3 == 4`), it automatically translates that
                # into something like `int.__eq__(3, 4)` instead of `(3).__eq__(4)` as an
                # optimization.
                #
                # While it normally it doesn't matter which of the two versions are used, it
                # does cause inconsistencies when working with classes. For example, translating
                # `int == int` to `int.__eq__(int)` would not work since `int.__eq__` is meant to
                # compare two int _instances_. What we really want is `type(int).__eq__`, which
                # is meant to compare two types or classes.
                #
                # This check makes sure that when we encounter an operator, we skip looking up
                # the corresponding method in the current instance to avoid this edge case.
                # See https://github.com/python/mypy/pull/1787 for more info.
                result = analyze_class_attribute_access(ret_type, name, node, is_lvalue,
                                                        builtin_type, not_ready_callback, msg,
                                                        original_type=original_type)
                if result:
                    return result
            # Look up from the 'type' type.
            return analyze_member_access(name, typ.fallback, node, is_lvalue, is_super,
                                         is_operator, builtin_type, not_ready_callback, msg,
                                         original_type=original_type, chk=chk)
        else:
            assert False, 'Unexpected type {}'.format(repr(ret_type))
    elif isinstance(typ, FunctionLike):
        # Look up from the 'function' type.
        return analyze_member_access(name, typ.fallback, node, is_lvalue, is_super,
                                     is_operator, builtin_type, not_ready_callback, msg,
                                     original_type=original_type, chk=chk)
    elif isinstance(typ, TypeVarType):
        return analyze_member_access(name, typ.upper_bound, node, is_lvalue, is_super,
                                     is_operator, builtin_type, not_ready_callback, msg,
                                     original_type=original_type, chk=chk)
    elif isinstance(typ, DeletedType):
        msg.deleted_as_rvalue(typ, node)
        return AnyType(TypeOfAny.from_error)
    elif isinstance(typ, TypeType):
        # Similar to FunctionLike + is_type_obj() above.
        item = None
        if isinstance(typ.item, Instance):
            item = typ.item
        elif isinstance(typ.item, AnyType):
            fallback = builtin_type('builtins.type')
            ignore_messages = msg.copy()
            ignore_messages.disable_errors()
            return analyze_member_access(name, fallback, node, is_lvalue, is_super,
                                     is_operator, builtin_type, not_ready_callback,
                                     ignore_messages, original_type=original_type, chk=chk)
        elif isinstance(typ.item, TypeVarType):
            if isinstance(typ.item.upper_bound, Instance):
                item = typ.item.upper_bound
        if item and not is_operator:
            # See comment above for why operators are skipped
            result = analyze_class_attribute_access(item, name, node, is_lvalue,
                                                    builtin_type, not_ready_callback, msg,
                                                    original_type=original_type)
            if result:
                return result
        fallback = builtin_type('builtins.type')
        if item is not None:
            fallback = item.type.metaclass_type or fallback
        return analyze_member_access(name, fallback, node, is_lvalue, is_super,
                                     is_operator, builtin_type, not_ready_callback, msg,
                                     original_type=original_type, chk=chk)

    if chk.should_suppress_optional_error([typ]):
        return AnyType(TypeOfAny.from_error)
    return msg.has_no_attr(original_type, typ, name, node)