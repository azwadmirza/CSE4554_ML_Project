def find_member(name: str, itype: Instance, subtype: Type) -> Optional[Type]:
    """Find the type of member by 'name' in 'itype's TypeInfo.

    Fin the member type after applying type arguments from 'itype', and binding
    'self' to 'subtype'. Return None if member was not found.
    """
    # TODO: this code shares some logic with checkmember.analyze_member_access,
    # consider refactoring.
    info = itype.type
    method = info.get_method(name)
    if method:
        if method.is_property:
            assert isinstance(method, OverloadedFuncDef)
            dec = method.items[0]
            assert isinstance(dec, Decorator)
            return find_node_type(dec.var, itype, subtype)
        return find_node_type(method, itype, subtype)
    else:
        # don't have such method, maybe variable or decorator?
        node = info.get(name)
        if not node:
            v = None
        else:
            v = node.node
        if isinstance(v, Decorator):
            v = v.var
        if isinstance(v, Var):
            return find_node_type(v, itype, subtype)
        if not v and name not in ['__getattr__', '__setattr__', '__getattribute__']:
            for method_name in ('__getattribute__', '__getattr__'):
                # Normally, mypy assumes that instances that define __getattr__ have all
                # attributes with the corresponding return type. If this will produce
                # many false negatives, then this could be prohibited for
                # structural subtyping.
                method = info.get_method(method_name)
                if method and method.info.fullname() != 'builtins.object':
                    getattr_type = get_proper_type(find_node_type(method, itype, subtype))
                    if isinstance(getattr_type, CallableType):
                        return getattr_type.ret_type
        if itype.type.fallback_to_any:
            return AnyType(TypeOfAny.special_form)
    return None