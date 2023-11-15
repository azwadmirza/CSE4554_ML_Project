def run(runner, args, write=sys.stdout.write):
    # Set up our logging handler
    logger.addHandler(LoggingHandler(args.color, write=write))
    logger.setLevel(logging.INFO)

    if args.no_stash or args.all_files:
        ctx = noop_context()
    else:
        ctx = staged_files_only(runner.cmd_runner)

    with ctx:
        if args.hook:
            return _run_hook(runner, args.hook, args, write=write)
        else:
            return _run_hooks(runner, args, write=write)