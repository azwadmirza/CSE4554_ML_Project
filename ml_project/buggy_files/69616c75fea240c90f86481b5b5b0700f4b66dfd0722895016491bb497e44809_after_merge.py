def _main(*args):
    from ..base.constants import SEARCH_PATH
    from ..base.context import context

    from ..gateways.logging import set_all_logger_level, set_verbosity

    if len(args) == 1:
        args = args + ('-h',)

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

    from .find_commands import find_commands

    def completer(prefix, **kwargs):
        return [i for i in list(sub_parsers.choices) + find_commands()
                if i.startswith(prefix)]

    # when using sys.argv, first argument is generally conda or __main__.py.  Ignore it.
    if (any(sname in args[0] for sname in ('conda', 'conda.exe', '__main__.py', 'conda-script.py'))
        and (args[1] in list(sub_parsers.choices.keys()) + find_commands()
             or args[1].startswith('-'))):
        log.debug("Ignoring first argument (%s), as it is not a subcommand", args[0])
        args = args[1:]

    sub_parsers.completer = completer
    args = p.parse_args(args)

    context.__init__(SEARCH_PATH, 'conda', args)

    if getattr(args, 'json', False):
        # Silence logging info to avoid interfering with JSON output
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