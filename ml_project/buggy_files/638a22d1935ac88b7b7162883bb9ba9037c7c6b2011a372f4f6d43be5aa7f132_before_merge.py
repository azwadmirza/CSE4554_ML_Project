def main(args, error):
    """ CLI entry point """
    del error  # unused

    # initialize libopenage
    from ..cppinterface.setup import setup
    setup(args)

    # conversion source
    if args.source_dir is not None:
        srcdir = CaseIgnoringDirectory(args.source_dir).root
    else:
        srcdir = None

    # Set verbosity for debug output
    if not args.debug_info:
        if args.devmode:
            args.debug_info = 3

        else:
            args.debug_info = 0

    # mount the config folder at "cfg/"
    from ..cvar.location import get_config_path
    from ..util.fslike.union import Union
    root = Union().root
    root["cfg"].mount(get_config_path())
    args.cfg_dir = root["cfg"]

    if args.interactive:
        interactive_browser(root["cfg"], srcdir)
        return 0

    # conversion target
    from ..assets import get_asset_path
    outdir = get_asset_path(args.output_dir)

    if args.force or wanna_convert() or conversion_required(outdir, args):
        if not convert_assets(outdir, args, srcdir):
            return 1
    else:
        print("assets are up to date; no conversion is required.")
        print("override with --force.")

    return 0