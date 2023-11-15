def refresh_suppressed_submodules(
        module: str,
        path: Optional[str],
        deps: Dict[str, Set[str]],
        graph: Graph,
        fscache: FileSystemCache,
        refresh_file: Callable[[str, str], List[str]]) -> Optional[List[str]]:
    """Look for submodules that are now suppressed in target package.

    If a submodule a.b gets added, we need to mark it as suppressed
    in modules that contain "from a import b". Previously we assumed
    that 'a.b' is not a module but a regular name.

    This is only relevant when following imports normally.

    Args:
        module: target package in which to look for submodules
        path: path of the module
        refresh_file: function that reads the AST of a module (returns error messages)

    Return a list of errors from refresh_file() if it was called. If the
    return value is None, we didn't call refresh_file().
    """
    messages = None
    if path is None or not path.endswith(INIT_SUFFIXES):
        # Only packages have submodules.
        return None
    # Find any submodules present in the directory.
    pkgdir = os.path.dirname(path)
    for fnam in fscache.listdir(pkgdir):
        if (not fnam.endswith(('.py', '.pyi'))
                or fnam.startswith("__init__.")
                or fnam.count('.') != 1):
            continue
        shortname = fnam.split('.')[0]
        submodule = module + '.' + shortname
        trigger = make_trigger(submodule)

        # We may be missing the required fine-grained deps.
        ensure_deps_loaded(module, deps, graph)

        if trigger in deps:
            for dep in deps[trigger]:
                # We can ignore <...> deps since a submodule can't trigger any.
                state = graph.get(dep)
                if not state:
                    # Maybe it's a non-top-level target. We only care about the module.
                    dep_module = module_prefix(graph, dep)
                    if dep_module is not None:
                        state = graph.get(dep_module)
                if state:
                    # Is the file may missing an AST in case it's read from cache?
                    if state.tree is None:
                        # Create AST for the file. This may produce some new errors
                        # that we need to propagate.
                        assert state.path is not None
                        messages = refresh_file(state.id, state.path)
                    tree = state.tree
                    assert tree  # Will be fine, due to refresh_file() above
                    for imp in tree.imports:
                        if isinstance(imp, ImportFrom):
                            if (imp.id == module
                                    and any(name == shortname for name, _ in imp.names)
                                    and submodule not in state.suppressed_set):
                                state.suppressed.append(submodule)
                                state.suppressed_set.add(submodule)
    return messages