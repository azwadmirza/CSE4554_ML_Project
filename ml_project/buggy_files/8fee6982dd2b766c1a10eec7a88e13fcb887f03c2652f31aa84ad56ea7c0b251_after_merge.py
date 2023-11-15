def find_targets_recursive(
        manager: BuildManager,
        graph: Graph,
        triggers: Set[str],
        deps: Dict[str, Set[str]],
        up_to_date_modules: Set[str]) -> Tuple[Dict[str, Set[FineGrainedDeferredNode]],
                                               Set[str], Set[TypeInfo]]:
    """Find names of all targets that need to reprocessed, given some triggers.

    Returns: A tuple containing a:
     * Dictionary from module id to a set of stale targets.
     * A set of module ids for unparsed modules with stale targets.
    """
    result = {}  # type: Dict[str, Set[FineGrainedDeferredNode]]
    worklist = triggers
    processed = set()  # type: Set[str]
    stale_protos = set()  # type: Set[TypeInfo]
    unloaded_files = set()  # type: Set[str]

    # Find AST nodes corresponding to each target.
    #
    # TODO: Don't rely on a set, since the items are in an unpredictable order.
    while worklist:
        processed |= worklist
        current = worklist
        worklist = set()
        for target in current:
            if target.startswith('<'):
                worklist |= deps.get(target, set()) - processed
            else:
                module_id = module_prefix(graph, target)
                if module_id is None:
                    # Deleted module.
                    continue
                if module_id in up_to_date_modules:
                    # Already processed.
                    continue
                if (module_id not in manager.modules
                        or manager.modules[module_id].is_cache_skeleton):
                    # We haven't actually parsed and checked the module, so we don't have
                    # access to the actual nodes.
                    # Add it to the queue of files that need to be processed fully.
                    unloaded_files.add(module_id)
                    continue

                if module_id not in result:
                    result[module_id] = set()
                manager.log_fine_grained('process: %s' % target)
                deferred, stale_proto = lookup_target(manager, target)
                if stale_proto:
                    stale_protos.add(stale_proto)
                result[module_id].update(deferred)

    return result, unloaded_files, stale_protos