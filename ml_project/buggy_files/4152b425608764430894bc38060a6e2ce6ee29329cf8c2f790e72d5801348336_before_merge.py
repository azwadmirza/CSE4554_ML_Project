def lookup_qualified_stnode(modules: Dict[str, MypyFile], name: str,
                            quick_and_dirty: bool) -> Optional[SymbolTableNode]:
    head = name
    rest = []
    while True:
        if '.' not in head:
            if not quick_and_dirty:
                assert '.' in head, "Cannot find %s" % (name,)
            return None
        head, tail = head.rsplit('.', 1)
        rest.append(tail)
        mod = modules.get(head)
        if mod is not None:
            break
    names = mod.names
    while True:
        if not rest:
            if not quick_and_dirty:
                assert rest, "Cannot find %s" % (name,)
            return None
        key = rest.pop()
        if key not in names:
            return None
        elif not quick_and_dirty:
            assert key in names, "Cannot find %s for %s" % (key, name)
        stnode = names[key]
        if not rest:
            return stnode
        node = stnode.node
        assert isinstance(node, TypeInfo)
        names = node.names