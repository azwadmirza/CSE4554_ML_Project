def convert_assets(assets, args, srcdir=None, prev_source_dir_path=None):
    """
    Perform asset conversion.

    Requires original assets and stores them in usable and free formats.

    assets must be a filesystem-like object pointing at the game's asset dir.
    srcdir must be None, or point at some source directory.

    If gen_extra_files is True, some more files, mostly for debugging purposes,
    are created.

    This method prepares srcdir and targetdir to allow a pleasant, unified
    conversion experience, then passes them to .driver.convert().
    """
    # acquire conversion source directory
    if srcdir is None:
        srcdir = acquire_conversion_source_dir(prev_source_dir_path)

    converted_path = assets / "converted"
    converted_path.mkdirs()
    targetdir = DirectoryCreator(converted_path).root

    # Set compression level for media output if it was not set
    if "compression_level" not in vars(args):
        args.compression_level = 1

    # Set verbosity for debug output
    if "debug_info" not in vars(args) or not args.debug_info:
        if args.devmode:
            args.debug_info = 3

        else:
            args.debug_info = 0

    # add a dir for debug info
    debug_log_path = converted_path / "debug" / datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    debugdir = DirectoryCreator(debug_log_path).root
    args.debugdir = AccessSynchronizer(debugdir).root

    # Create CLI args info
    debug_cli_args(args.debugdir, args.debug_info, args)

    # Initialize game versions data
    auxiliary_files_dir = args.cfg_dir / "converter" / "games"
    args.avail_game_eds, args.avail_game_exps = create_version_objects(auxiliary_files_dir)

    # Acquire game version info
    args.game_version = get_game_version(srcdir, args.avail_game_eds, args.avail_game_exps)
    debug_game_version(args.debugdir, args.debug_info, args)

    # Mount assets into conversion folder
    data_dir = mount_asset_dirs(srcdir, args.game_version)
    if not data_dir:
        return None

    # make srcdir and targetdir safe for threaded conversion
    args.srcdir = AccessSynchronizer(data_dir).root
    args.targetdir = AccessSynchronizer(targetdir).root

    # Create mountpoint info
    debug_mounts(args.debugdir, args.debug_info, args)

    def flag(name):
        """
        Convenience function for accessing boolean flags in args.
        Flags default to False if they don't exist.
        """
        return getattr(args, name, False)

    args.flag = flag

    # import here so codegen.py doesn't depend on it.
    from .tool.driver import convert

    converted_count = 0
    total_count = None
    for current_item in convert(args):
        if isinstance(current_item, int):
            # convert is informing us about the estimated number of remaining
            # items.
            total_count = current_item + converted_count
            continue

        # TODO a GUI would be nice here.

        if total_count is None:
            info("[%s] %s", converted_count, current_item)
        else:
            info("[%s] %s", format_progress(converted_count, total_count), current_item)

        converted_count += 1

    # clean args
    del args.srcdir
    del args.targetdir

    return data_dir.resolve_native_path()