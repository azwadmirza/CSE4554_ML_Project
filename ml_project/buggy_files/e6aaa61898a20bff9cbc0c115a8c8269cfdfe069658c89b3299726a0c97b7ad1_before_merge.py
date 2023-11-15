def get_asset_path(args):
    """
    Returns a Path object for the game assets.

    args are the arguments, as provided by the CLI's ArgumentParser.
    """

    # if we're in devmode, use only the build source asset folder
    if not args.asset_dir and config.DEVMODE:
        return Directory(os.path.join(config.BUILD_SRC_DIR, "assets")).root

    # else, mount the possible locations in an union:
    # overlay the global dir and the user dir.
    result = Union().root

    # the cmake-determined folder for storing assets
    global_data = Path(config.GLOBAL_ASSET_DIR)
    if global_data.is_dir():
        result.mount(WriteBlocker(Directory(global_data).root).root)

    # user-data directory as provided by environment variables
    # and platform standards
    # we always create this!
    home_data = default_dirs.get_dir("data_home") / "openage"
    result.mount(
        Directory(
            home_data,
            create_if_missing=True
        ).root / "assets"
    )

    # the program argument overrides it all
    if args.asset_dir:
        result.mount(Directory(args.asset_dir).root)

    return result