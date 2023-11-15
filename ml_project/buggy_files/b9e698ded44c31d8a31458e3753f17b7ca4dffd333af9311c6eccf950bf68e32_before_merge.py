def _main():
    log.debug("conda.cli.main called with %s", sys.argv)
    if len(sys.argv) > 1:
        argv1 = sys.argv[1]
        if argv1 in ('..activate', '..deactivate', '..checkenv', '..changeps1'):
            import conda.cli.activate as activate
            activate.main()
            return
        if argv1 in ('activate', 'deactivate'):

            message = "'%s' is not a conda command.\n" % argv1
            if not on_win:
                message += ' Did you mean "source %s" ?\n' % ' '.join(sys.argv[1:])

            raise CommandNotFoundError(argv1, message)

    if len(sys.argv) == 1:
        sys.argv.append('-h')

    p, sub_parsers = generate_parser()

    main_modules = ["info", "help", "list", "search", "create", "install", "update",
                    "remove", "config", "clean", "package"]
    modules = ["conda.cli.main_"+suffix for suffix in main_modules]
    for module in modules:
        imported = importlib.import_module(module)
        imported.configure_parser(sub_parsers)
        if "update" in module:
            imported.configure_parser(sub_parsers, name='upgrade')
        if "remove" in module:
            imported.configure_parser(sub_parsers, name='uninstall')

    from conda.cli.find_commands import find_commands

    def completer(prefix, **kwargs):
        return [i for i in list(sub_parsers.choices) + find_commands()
                if i.startswith(prefix)]

    sub_parsers.completer = completer
    args = p.parse_args()

    context._add_argparse_args(args)

    if getattr(args, 'json', False):
        # # Silence logging info to avoid interfering with JSON output
        # for logger in Logger.manager.loggerDict:
        #     if logger not in ('fetch', 'progress'):
        #         getLogger(logger).setLevel(CRITICAL + 1)
        for logger in ('print', 'dotupdate', 'stdoutlog', 'stderrlog'):
            getLogger(logger).setLevel(CRITICAL + 1)

    if context.debug:
        set_all_logger_level(DEBUG)
    elif context.verbosity:
        set_verbosity(context.verbosity)
        log.debug("verbosity set to %s", context.verbosity)

    exit_code = args.func(args, p)
    if isinstance(exit_code, int):
        return exit_code