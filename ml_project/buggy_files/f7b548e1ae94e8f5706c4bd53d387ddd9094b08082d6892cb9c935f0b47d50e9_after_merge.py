def reprocess_nodes(manager: BuildManager,
                    graph: Dict[str, State],
                    module_id: str,
                    nodeset: Set[FineGrainedDeferredNode],
                    deps: Dict[str, Set[str]]) -> Set[str]:
    """Reprocess a set of nodes within a single module.

    Return fired triggers.
    """
    if module_id not in graph:
        manager.log_fine_grained('%s not in graph (blocking errors or deleted?)' %
                    module_id)
        return set()

    file_node = manager.modules[module_id]
    old_symbols = find_symbol_tables_recursive(file_node.fullname(), file_node.names)
    old_symbols = {name: names.copy() for name, names in old_symbols.items()}
    old_symbols_snapshot = snapshot_symbol_table(file_node.fullname(), file_node.names)

    def key(node: FineGrainedDeferredNode) -> int:
        # Unlike modules which are sorted by name within SCC,
        # nodes within the same module are sorted by line number, because
        # this is how they are processed in normal mode.
        return node.node.line

    nodes = sorted(nodeset, key=key)

    options = graph[module_id].options
    manager.errors.set_file_ignored_lines(
        file_node.path, file_node.ignored_lines, options.ignore_errors)

    targets = set()
    for node in nodes:
        target = target_from_node(module_id, node.node)
        if target is not None:
            targets.add(target)
    manager.errors.clear_errors_in_targets(file_node.path, targets)

    # Strip semantic analysis information.
    for deferred in nodes:
        strip_target(deferred.node)
    semantic_analyzer = manager.semantic_analyzer

    patches = []  # type: List[Tuple[int, Callable[[], None]]]

    # Second pass of semantic analysis. We don't redo the first pass, because it only
    # does local things that won't go stale.
    for deferred in nodes:
        with semantic_analyzer.file_context(
                file_node=file_node,
                fnam=file_node.path,
                options=options,
                active_type=deferred.active_typeinfo):
            manager.semantic_analyzer.refresh_partial(deferred.node, patches)

    # Third pass of semantic analysis.
    for deferred in nodes:
        with semantic_analyzer.file_context(
                file_node=file_node,
                fnam=file_node.path,
                options=options,
                active_type=deferred.active_typeinfo,
                scope=manager.semantic_analyzer_pass3.scope):
            manager.semantic_analyzer_pass3.refresh_partial(deferred.node, patches)

    with semantic_analyzer.file_context(
            file_node=file_node,
            fnam=file_node.path,
            options=options,
            active_type=None):
        apply_semantic_analyzer_patches(patches)

    # Merge symbol tables to preserve identities of AST nodes. The file node will remain
    # the same, but other nodes may have been recreated with different identities, such as
    # NamedTuples defined using assignment statements.
    new_symbols = find_symbol_tables_recursive(file_node.fullname(), file_node.names)
    for name in old_symbols:
        if name in new_symbols:
            merge_asts(file_node, old_symbols[name], file_node, new_symbols[name])

    # Type check.
    checker = graph[module_id].type_checker()
    checker.reset()
    # We seem to need additional passes in fine-grained incremental mode.
    checker.pass_num = 0
    checker.last_pass = 3
    more = checker.check_second_pass(nodes)
    while more:
        more = False
        if graph[module_id].type_checker().check_second_pass():
            more = True

    new_symbols_snapshot = snapshot_symbol_table(file_node.fullname(), file_node.names)
    # Check if any attribute types were changed and need to be propagated further.
    changed = compare_symbol_table_snapshots(file_node.fullname(),
                                             old_symbols_snapshot,
                                             new_symbols_snapshot)
    new_triggered = {make_trigger(name) for name in changed}

    # Dependencies may have changed.
    update_deps(module_id, nodes, graph, deps, options)

    # Report missing imports.
    graph[module_id].verify_dependencies()

    return new_triggered