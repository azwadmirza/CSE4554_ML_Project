def get_asset_path(custom_asset_dir=None):
    """
    Returns a Path object for the game assets.

    `custom_asset_dir` can a custom asset directory, which is mounted at the
    top of the union filesystem (i.e. has highest priority).

    This function is used by the both the conversion process
    and the game startup. The conversion uses it for its output,
    the game as its data source(s).
    """

    # if we're in devmode, use only the in-repo asset folder
    if not custom_asset_dir and config.DEVMODE:
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
    if custom_asset_dir:
        result.mount(Directory(custom_asset_dir).root)

    return result