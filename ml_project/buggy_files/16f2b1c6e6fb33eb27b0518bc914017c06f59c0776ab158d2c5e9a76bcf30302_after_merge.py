def execute(args, parser):
    name = args.remote_definition or args.name

    try:
        spec = install_specs.detect(name=name, filename=args.file,
                                    directory=os.getcwd())
        env = spec.environment
    except exceptions.SpecNotFound as e:
        common.error_and_exit(str(e), json=args.json)

    if not args.name:
        if not env.name:
                    # Note, this is a hack fofr get_prefix that assumes argparse results
            # TODO Refactor common.get_prefix
            name = os.environ.get('CONDA_DEFAULT_ENV', False)
            if not name:
                msg = "Unable to determine environment\n\n"
                msg += textwrap.dedent("""
                    Please re-run this command with one of the following options:

                    * Provide an environment name via --name or -n
                    * Re-run this command inside an activated conda environment.""").lstrip()
                # TODO Add json support
                common.error_and_exit(msg, json=False)

        # Note: stubbing out the args object as all of the
        # conda.cli.common code thinks that name will always
        # be specified.
        args.name = env.name

    prefix = common.get_prefix(args, search=False)
    # CAN'T Check with this function since it assumes we will create prefix.
    # cli_install.check_prefix(prefix, json=args.json)

    # TODO, add capability
    # common.ensure_override_channels_requires_channel(args)
    # channel_urls = args.channel or ()

    for installer_type, specs in env.dependencies.items():
        try:
            installer = get_installer(installer_type)
            installer.install(prefix, specs, args, env)
        except InvalidInstaller:
            sys.stderr.write(textwrap.dedent("""
                Unable to install package for {0}.

                Please double check and ensure you dependencies file has
                the correct spelling.  You might also try installing the
                conda-env-{0} package to see if provides the required
                installer.
                """).lstrip().format(installer_type)
            )
            return -1

    touch_nonadmin(prefix)
    if not args.json:
        cli_install.print_activate(args.name if args.name else prefix)