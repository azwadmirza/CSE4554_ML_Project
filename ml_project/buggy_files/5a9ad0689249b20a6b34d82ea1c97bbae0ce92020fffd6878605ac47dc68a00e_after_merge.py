def execute(args, parser):
    if not args.name:
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
            error_and_exit(msg, json=False)
        args.name = name
    else:
        name = args.name
    prefix = get_prefix(args)
    env = from_environment(name, prefix, no_builds=args.no_builds,
                           ignore_channels=args.ignore_channels)

    if args.override_channels:
        env.remove_channels()

    if args.channel is not None:
        env.add_channels(args.channel)

    if args.file is None:
        print(env.to_yaml())
    else:
        fp = open(args.file, 'wb')
        env.to_yaml(stream=fp)