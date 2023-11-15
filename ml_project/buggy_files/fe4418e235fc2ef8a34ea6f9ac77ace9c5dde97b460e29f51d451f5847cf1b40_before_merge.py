def lookup_target(manager: BuildManager,
                  target: str) -> Tuple[List[DeferredNode], Optional[TypeInfo]]:
    """Look up a target by fully-qualified name.

    The first item in the return tuple is a list of deferred nodes that
    needs to be reprocessed. If the target represents a TypeInfo corresponding
    to a protocol, return it as a second item in the return tuple, otherwise None.
    """
    def not_found() -> None:
        manager.log_fine_grained(
            "Can't find matching target for %s (stale dependency?)" % target)

    modules = manager.modules
    items = split_target(modules, target)
    if items is None:
        not_found()  # Stale dependency
        return [], None
    module, rest = items
    if rest:
        components = rest.split('.')
    else:
        components = []
    node = modules[module]  # type: Optional[SymbolNode]
    file = None  # type: Optional[MypyFile]
    active_class = None
    active_class_name = None
    for c in components:
        if isinstance(node, TypeInfo):
            active_class = node
            active_class_name = node.name()
        if isinstance(node, MypyFile):
            file = node
        if (not isinstance(node, (MypyFile, TypeInfo))
                or c not in node.names):
            not_found()  # Stale dependency
            return [], None
        node = node.names[c].node
    if isinstance(node, TypeInfo):
        # A ClassDef target covers the body of the class and everything defined
        # within it.  To get the body we include the entire surrounding target,
        # typically a module top-level, since we don't support processing class
        # bodies as separate entitites for simplicity.
        assert file is not None
        if node.fullname() != target:
            # This is a reference to a different TypeInfo, likely due to a stale dependency.
            # Processing them would spell trouble -- for example, we could be refreshing
            # a deserialized TypeInfo with missing attributes.
            not_found()
            return [], None
        result = [DeferredNode(file, None, None)]
        stale_info = None  # type: Optional[TypeInfo]
        if node.is_protocol:
            stale_info = node
        for name, symnode in node.names.items():
            node = symnode.node
            if isinstance(node, FuncDef):
                method, _ = lookup_target(manager, target + '.' + name)
                result.extend(method)
        return result, stale_info
    if isinstance(node, Decorator):
        # Decorator targets actually refer to the function definition only.
        node = node.func
    if not isinstance(node, (FuncDef,
                             MypyFile,
                             OverloadedFuncDef)):
        # The target can't be refreshed. It's possible that the target was
        # changed to another type and we have a stale dependency pointing to it.
        not_found()
        return [], None
    if node.fullname() != target:
        # Stale reference points to something unexpected. We shouldn't process since the
        # context will be wrong and it could be a partially initialized deserialized node.
        not_found()
        return [], None
    return [DeferredNode(node, active_class_name, active_class)], None