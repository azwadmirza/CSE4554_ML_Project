def execute(args, parser):

    if not (args.all or args.package_names):
        raise CondaValueError('no package names supplied,\n'
                              '       try "conda remove -h" for more details')

    prefix = context.target_prefix
    check_non_admin()

    if args.all and prefix == context.default_prefix:
        msg = "cannot remove current environment. deactivate and run conda remove again"
        raise CondaEnvironmentError(msg)
    if args.all and not isdir(prefix):
        # full environment removal was requested, but environment doesn't exist anyway
        return 0

    if not is_conda_environment(prefix):
        from ..exceptions import EnvironmentLocationNotFound
        raise EnvironmentLocationNotFound(prefix)

    delete_trash()
    if args.all:
        if prefix == context.root_prefix:
            raise CondaEnvironmentError('cannot remove root environment,\n'
                                        '       add -n NAME or -p PREFIX option')
        print("\nRemove all packages in environment %s:\n" % prefix, file=sys.stderr)

        index = linked_data(prefix)
        index = {dist: info for dist, info in iteritems(index)}

        actions = defaultdict(list)
        actions[PREFIX] = prefix
        for dist in sorted(iterkeys(index)):
            add_unlink(actions, dist)
        actions['ACTION'] = 'REMOVE_ALL'
        action_groups = (actions, index),

        if not context.json:
            confirm_yn()
        rm_rf(prefix)

        if context.json:
            stdout_json({
                'success': True,
                'actions': tuple(x[0] for x in action_groups)
            })
        return

    else:
        specs = specs_from_args(args.package_names)
        channel_urls = ()
        subdirs = ()
        solver = Solver(prefix, channel_urls, subdirs, specs_to_remove=specs)
        txn = solver.solve_for_transaction(force_remove=args.force)
        pfe = txn.get_pfe()
        handle_txn(pfe, txn, prefix, args, False, True)