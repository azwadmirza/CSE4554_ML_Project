def execute(args, parser):
    import conda.plan as plan
    import conda.instructions as inst
    from conda.gateways.disk.delete import rm_rf
    from conda.core.linked_data import linked_data

    if not (args.all or args.package_names):
        raise CondaValueError('no package names supplied,\n'
                              '       try "conda remove -h" for more details')

    prefix = context.prefix_w_legacy_search
    if args.all and prefix == context.default_prefix:
        msg = "cannot remove current environment. deactivate and run conda remove again"
        raise CondaEnvironmentError(msg)
    check_write('remove', prefix, json=context.json)
    ensure_use_local(args)
    ensure_override_channels_requires_channel(args)
    if not args.features and args.all:
        index = linked_data(prefix)
        index = {dist: info for dist, info in iteritems(index)}
    else:
        index = get_index(channel_urls=context.channels,
                          prepend=not args.override_channels,
                          use_local=args.use_local,
                          use_cache=args.use_index_cache,
                          prefix=prefix)
    specs = None
    if args.features:
        specs = ['@' + f for f in set(args.package_names)]
        actions = plan.remove_actions(prefix, specs, index, pinned=args.pinned)
        action_groups = actions,
    elif args.all:
        if plan.is_root_prefix(prefix):
            raise CondaEnvironmentError('cannot remove root environment,\n'
                                        '       add -n NAME or -p PREFIX option')
        actions = {inst.PREFIX: prefix}
        for dist in sorted(iterkeys(index)):
            plan.add_unlink(actions, dist)
        action_groups = actions,
    else:
        specs = specs_from_args(args.package_names)
        r = Resolve(index)
        prefix_spec_map = create_prefix_spec_map_with_deps(r, specs, prefix)

        if (context.conda_in_root and plan.is_root_prefix(prefix) and names_in_specs(
                ROOT_NO_RM, specs) and not args.force):
            raise CondaEnvironmentError('cannot remove %s from root environment' %
                                        ', '.join(ROOT_NO_RM))
        actions = []
        for prfx, spcs in iteritems(prefix_spec_map):
            index = linked_data(prfx)
            index = {dist: info for dist, info in iteritems(index)}
            actions.append(plan.remove_actions(prfx, list(spcs), index=index, force=args.force,
                                               pinned=args.pinned))
        action_groups = tuple(actions)

    delete_trash()
    if any(plan.nothing_to_do(actions) for actions in action_groups):
        if args.all:
            print("\nRemove all packages in environment %s:\n" % prefix, file=sys.stderr)
            if not context.json:
                confirm_yn(args)
            rm_rf(prefix)

            if context.json:
                stdout_json({
                    'success': True,
                    'actions': action_groups
                })
            return
        error_message = 'no packages found to remove from environment: %s' % prefix
        raise PackageNotFoundError(error_message)
    for action in action_groups:
        if not context.json:
            print()
            print("Package plan for package removal in environment %s:" % action["PREFIX"])
            plan.display_actions(action, index)

        if context.json and args.dry_run:
            stdout_json({
                'success': True,
                'dry_run': True,
                'actions': action_groups
            })
            return

    if not context.json:
        confirm_yn(args)

    for actions in action_groups:
        if context.json and not context.quiet:
            with json_progress_bars():
                plan.execute_actions(actions, index, verbose=not context.quiet)
        else:
            plan.execute_actions(actions, index, verbose=not context.quiet)
            if specs:
                try:
                    with open(join(prefix, 'conda-meta', 'history'), 'a') as f:
                        f.write('# remove specs: %s\n' % ','.join(specs))
                except IOError as e:
                    if e.errno == errno.EACCES:
                        log.debug("Can't write the history file")
                    else:
                        raise

        target_prefix = actions["PREFIX"]
        if (is_private_env(prefix_to_env_name(target_prefix, context.root_prefix)) and
                linked_data(target_prefix) == {}):
            rm_rf(target_prefix)

    if args.all:
        rm_rf(prefix)

    if context.json:
        stdout_json({
            'success': True,
            'actions': actions
        })