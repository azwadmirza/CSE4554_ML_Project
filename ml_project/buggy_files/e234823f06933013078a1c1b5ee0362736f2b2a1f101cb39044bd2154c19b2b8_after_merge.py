def install_actions_list(prefix, index, specs, force=False, only_names=None, always_copy=False,
                         pinned=True, minimal_hint=False, update_deps=True, prune=False,
                         channel_priority_map=None, is_update=False):
    # type: (str, Dict[Dist, Record], List[str], bool, Option[List[str]], bool, bool, bool,
    #        bool, bool, bool, Dict[str, Sequence[str, int]]) -> List[Dict[weird]]
    specs = [MatchSpec(spec) for spec in specs]
    r = get_resolve_object(index.copy(), prefix)

    linked_in_root = linked_data(context.root_prefix)

    dists_for_envs = determine_all_envs(r, specs, channel_priority_map=channel_priority_map)
    ensure_packge_not_duplicated_in_private_env_root(dists_for_envs, linked_in_root)
    preferred_envs = set(d.env for d in dists_for_envs)

    # Group specs by prefix
    grouped_specs = determine_dists_per_prefix(r, prefix, index, preferred_envs,
                                               dists_for_envs, context)

    # Replace SpecsForPrefix specs with specs that were passed in in order to retain
    #   version information
    required_solves = match_to_original_specs(specs, grouped_specs)

    actions = [get_actions_for_dists(specs_by_prefix, only_names, index, force,
                                     always_copy, prune, update_deps, pinned)
               for specs_by_prefix in required_solves]

    # Need to add unlink actions if updating a private env from root
    if is_update and prefix == context.root_prefix:
        add_unlink_options_for_update(actions, required_solves, index)

    return actions