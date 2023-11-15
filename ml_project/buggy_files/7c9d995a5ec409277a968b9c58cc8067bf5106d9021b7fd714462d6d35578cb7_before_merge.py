def locals_import_from(node, locals_):
    # Don't add future imports to locals.
    if node.modname == '__future__':
        return

    # Sort the list for having the locals ordered by their first
    # appearance.
    def sort_locals(my_list):
        my_list.sort(key=lambda node: node.fromlineno)

    for name, asname in node.names:
        if name == '*':
            try:
                imported = util.do_import_module(node, node.modname)
            except exceptions.AstroidBuildingError:
                continue
            for name in imported.wildcard_import_names():
                locals_[name].append(node)
                sort_locals(locals_[name])
        else:
            locals_[asname or name].append(node)
            sort_locals(locals_[asname or name])