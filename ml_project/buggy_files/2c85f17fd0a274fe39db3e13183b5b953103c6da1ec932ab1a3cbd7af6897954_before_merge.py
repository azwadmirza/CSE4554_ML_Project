def analyze_type_alias(node: Expression,
                       lookup_func: Callable[[str, Context], SymbolTableNode],
                       lookup_fqn_func: Callable[[str], SymbolTableNode],
                       tvar_scope: TypeVarScope,
                       fail_func: Callable[[str, Context], None],
                       plugin: Plugin,
                       options: Options,
                       is_typeshed_stub: bool,
                       allow_unnormalized: bool = False) -> Optional[Type]:
    """Return type if node is valid as a type alias rvalue.

    Return None otherwise. 'node' must have been semantically analyzed.
    """
    # Quickly return None if the expression doesn't look like a type. Note
    # that we don't support straight string literals as type aliases
    # (only string literals within index expressions).
    if isinstance(node, RefExpr):
        # Note that this misses the case where someone tried to use a
        # class-referenced type variable as a type alias.  It's easier to catch
        # that one in checkmember.py
        if node.kind == TVAR:
            fail_func('Type variable "{}" is invalid as target for type alias'.format(
                node.fullname), node)
            return None
        if not (isinstance(node.node, TypeInfo) or
                node.fullname == 'typing.Any' or
                node.kind == TYPE_ALIAS):
            return None
    elif isinstance(node, IndexExpr):
        base = node.base
        if isinstance(base, RefExpr):
            if not (isinstance(base.node, TypeInfo) or
                    base.fullname in type_constructors or
                    base.kind == TYPE_ALIAS):
                return None
            # Enums can't be generic, and without this check we may incorrectly interpret indexing
            # an Enum class as creating a type alias.
            if isinstance(base.node, TypeInfo) and base.node.is_enum:
                return None
        else:
            return None
    elif isinstance(node, CallExpr):
        if (isinstance(node.callee, NameExpr) and len(node.args) == 1 and
                isinstance(node.args[0], NameExpr)):
            call = lookup_func(node.callee.name, node.callee)
            arg = lookup_func(node.args[0].name, node.args[0])
            if (call is not None and call.node and call.node.fullname() == 'builtins.type' and
                    arg is not None and arg.node and arg.node.fullname() == 'builtins.None'):
                return NoneTyp()
            return None
        return None
    else:
        return None

    # It's a type alias (though it may be an invalid one).
    try:
        type = expr_to_unanalyzed_type(node)
    except TypeTranslationError:
        fail_func('Invalid type alias', node)
        return None
    analyzer = TypeAnalyser(lookup_func, lookup_fqn_func, tvar_scope, fail_func, plugin, options,
                            is_typeshed_stub, aliasing=True, allow_unnormalized=allow_unnormalized)
    return type.accept(analyzer)