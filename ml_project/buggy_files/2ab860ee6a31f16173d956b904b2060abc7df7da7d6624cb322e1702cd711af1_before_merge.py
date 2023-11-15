def run(runner, args, write=sys.stdout.write, environ=os.environ):
    # Set up our logging handler
    logger.addHandler(LoggingHandler(args.color, write=write))
    logger.setLevel(logging.INFO)

    # Check if we have unresolved merge conflict files and fail fast.
    if _has_unmerged_paths(runner):
        logger.error('Unmerged files.  Resolve before committing.')
        return 1

    if args.no_stash or args.all_files:
        ctx = noop_context()
    else:
        ctx = staged_files_only(runner.cmd_runner)

    with ctx:
        if args.hook:
            return _run_hook(runner, args, write=write)
        else:
            return _run_hooks(runner, args, write=write, environ=environ)