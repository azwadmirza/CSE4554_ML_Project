def execute(args, parser):
    from conda.base.context import context
    name = args.remote_definition or args.name

    try:
        spec = specs.detect(name=name, filename=expand(args.file),
                            directory=os.getcwd())
        env = spec.environment

        # FIXME conda code currently requires args to have a name or prefix
        # don't overwrite name if it's given. gh-254
        if args.prefix is None and args.name is None:
            args.name = env.name

    except exceptions.SpecNotFound:
        raise

    prefix = get_prefix(args, search=False)

    if args.force and prefix != context.root_prefix and os.path.exists(prefix):
        rm_rf(prefix)
    cli_install.check_prefix(prefix, json=args.json)

    # TODO, add capability
    # common.ensure_override_channels_requires_channel(args)
    # channel_urls = args.channel or ()

    # # special case for empty environment
    # if not env.dependencies:
    #     from conda.install import symlink_conda
    #     symlink_conda(prefix, context.root_dir)

    for installer_type, pkg_specs in env.dependencies.items():
        try:
            installer = get_installer(installer_type)
            installer.install(prefix, pkg_specs, args, env)
        except InvalidInstaller:
            sys.stderr.write(textwrap.dedent("""
                Unable to install package for {0}.

                Please double check and ensure your dependencies file has
                the correct spelling.  You might also try installing the
                conda-env-{0} package to see if provides the required
                installer.
                """).lstrip().format(installer_type)
            )
            return -1

    touch_nonadmin(prefix)
    cli_install.print_activate(args.name if args.name else prefix)