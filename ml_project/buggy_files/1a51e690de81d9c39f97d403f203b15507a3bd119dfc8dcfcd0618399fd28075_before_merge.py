def parseArgs(vd, parser:argparse.ArgumentParser):
    addOptions(parser)
    args, remaining = parser.parse_known_args()

    # add visidata_dir to path before loading config file (can only be set from cli)
    sys.path.append(str(visidata.Path(args.visidata_dir or options.visidata_dir)))

    # import plugins from .visidata/plugins before .visidatarc, so plugin options can be overridden
    for modname in args.imports.split():
        addGlobals(importlib.import_module(modname).__dict__)

    # user customisations in config file in standard location
    loadConfigFile(visidata.Path(args.config or options.config), getGlobals())

    # add plugin options and reparse
    addOptions(parser)
    args, remaining = parser.parse_known_args()

    # apply command-line overrides after .visidatarc
    for optname, optval in vars(args).items():
        if optval is not None and optname not in ['inputs', 'play', 'batch', 'output', 'diff']:
            options[optname] = optval

    return args