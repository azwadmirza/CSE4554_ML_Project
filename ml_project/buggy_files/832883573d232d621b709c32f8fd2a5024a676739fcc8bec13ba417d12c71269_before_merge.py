def main(
        # pylint: disable=too-many-locals,too-many-return-statements
        # pylint: disable=too-many-branches,too-many-statements
):
    """initialize objects and run the filemanager"""
    import ranger.api
    from ranger.container.settings import Settings
    from ranger.core.shared import FileManagerAware, SettingsAware
    from ranger.core.fm import FM
    from ranger.ext.logutils import setup_logging
    from ranger.ext.openstruct import OpenStruct

    ranger.args = args = parse_arguments()
    ranger.arg = OpenStruct(args.__dict__)  # COMPAT
    setup_logging(debug=args.debug, logfile=args.logfile)

    for line in VERSION_MSG:
        LOG.info(line)
    LOG.info('Process ID: %s', os.getpid())

    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        print("Warning: Unable to set locale.  Expect encoding problems.")

    # so that programs can know that ranger spawned them:
    level = 'RANGER_LEVEL'
    if level in os.environ and os.environ[level].isdigit():
        os.environ[level] = str(int(os.environ[level]) + 1)
    else:
        os.environ[level] = '1'

    if 'SHELL' not in os.environ:
        os.environ['SHELL'] = 'sh'

    LOG.debug("cache dir: '%s'", args.cachedir)
    LOG.debug("config dir: '%s'", args.confdir)
    LOG.debug("data dir: '%s'", args.datadir)

    if args.copy_config is not None:
        fm = FM()
        fm.copy_config_files(args.copy_config)
        return 0
    if args.list_tagged_files:
        if args.clean:
            print("Can't access tag data in clean mode", file=sys.stderr)
            return 1
        fm = FM()
        try:
            if sys.version_info[0] >= 3:
                fobj = open(fm.datapath('tagged'), 'r', errors='replace')
            else:
                fobj = open(fm.datapath('tagged'), 'r')
        except OSError as ex:
            print('Unable to open `tagged` data file: {0}'.format(ex), file=sys.stderr)
            return 1
        for line in fobj.readlines():
            if len(line) > 2 and line[1] == ':':
                if line[0] in args.list_tagged_files:
                    sys.stdout.write(line[2:])
            elif line and '*' in args.list_tagged_files:
                sys.stdout.write(line)
        return 0

    SettingsAware.settings_set(Settings())

    if args.selectfile:
        args.selectfile = os.path.abspath(args.selectfile)
        args.paths.insert(0, os.path.dirname(args.selectfile))

    if args.paths:
        paths = [p[7:] if p.startswith('file:///') else p for p in args.paths]
    else:
        paths = [os.environ.get('PWD', os.getcwd())]
    paths_inaccessible = []
    for path in paths:
        try:
            path_abs = os.path.abspath(path)
        except OSError:
            paths_inaccessible += [path]
            continue
        if not os.access(path_abs, os.F_OK):
            paths_inaccessible += [path]
    if paths_inaccessible:
        print('Inaccessible paths: {0}'.format(paths), file=sys.stderr)
        return 1

    profile = None
    exit_msg = ''
    exit_code = 0
    try:  # pylint: disable=too-many-nested-blocks
        # Initialize objects
        fm = FM(paths=paths)
        FileManagerAware.fm_set(fm)
        load_settings(fm, args.clean)

        if args.show_only_dirs:
            from ranger.container.directory import InodeFilterConstants
            fm.settings.global_inode_type_filter = InodeFilterConstants.DIRS

        if args.list_unused_keys:
            from ranger.ext.keybinding_parser import (special_keys,
                                                      reversed_special_keys)
            maps = fm.ui.keymaps['browser']
            for key in sorted(special_keys.values(), key=str):
                if key not in maps:
                    print("<%s>" % reversed_special_keys[key])
            for key in range(33, 127):
                if key not in maps:
                    print(chr(key))
            return 0

        if not sys.stdin.isatty():
            sys.stderr.write("Error: Must run ranger from terminal\n")
            raise SystemExit(1)

        if fm.username == 'root':
            fm.settings.preview_files = False
            fm.settings.use_preview_script = False
            LOG.info("Running as root, disabling the file previews.")
        if not args.debug:
            from ranger.ext import curses_interrupt_handler
            curses_interrupt_handler.install_interrupt_handler()

        # Create cache directory
        if fm.settings.preview_images and fm.settings.use_preview_script:
            if not os.path.exists(args.cachedir):
                os.makedirs(args.cachedir)

        if not args.clean:
            # Create data directory
            if not os.path.exists(args.datadir):
                os.makedirs(args.datadir)

            # Restore saved tabs
            tabs_datapath = fm.datapath('tabs')
            if fm.settings.save_tabs_on_exit and os.path.exists(tabs_datapath) and not args.paths:
                try:
                    with open(tabs_datapath, 'r') as fobj:
                        tabs_saved = fobj.read().partition('\0\0')
                        fm.start_paths += tabs_saved[0].split('\0')
                    if tabs_saved[-1]:
                        with open(tabs_datapath, 'w') as fobj:
                            fobj.write(tabs_saved[-1])
                    else:
                        os.remove(tabs_datapath)
                except OSError as ex:
                    LOG.error('Unable to restore saved tabs')
                    LOG.exception(ex)

        # Run the file manager
        fm.initialize()
        ranger.api.hook_init(fm)
        fm.ui.initialize()

        if args.selectfile:
            fm.select_file(args.selectfile)

        if args.cmd:
            for command in args.cmd:
                fm.execute_console(command)

        if ranger.args.profile:
            import cProfile
            import pstats
            ranger.__fm = fm  # pylint: disable=protected-access
            profile_file = tempfile.gettempdir() + '/ranger_profile'
            cProfile.run('ranger.__fm.loop()', profile_file)
            profile = pstats.Stats(profile_file, stream=sys.stderr)
        else:
            fm.loop()

    except Exception:  # pylint: disable=broad-except
        import traceback
        ex_traceback = traceback.format_exc()
        exit_msg += '\n'.join(VERSION_MSG) + '\n'
        try:
            exit_msg += "Current file: {0}\n".format(repr(fm.thisfile.path))
        except Exception:  # pylint: disable=broad-except
            pass
        exit_msg += '''
{0}
ranger crashed. Please report this traceback at:
https://github.com/ranger/ranger/issues
'''.format(ex_traceback)

        exit_code = 1

    except SystemExit as ex:
        if ex.code is not None:
            if not isinstance(ex.code, int):
                exit_msg = ex.code
                exit_code = 1
            else:
                exit_code = ex.code

    finally:
        if exit_msg:
            LOG.critical(exit_msg)
        try:
            fm.ui.destroy()
        except (AttributeError, NameError):
            pass
        # If profiler is enabled print the stats
        if ranger.args.profile and profile:
            profile.strip_dirs().sort_stats('cumulative').print_callees()
        # print the exit message if any
        if exit_msg:
            sys.stderr.write(exit_msg)
        return exit_code  # pylint: disable=lost-exception