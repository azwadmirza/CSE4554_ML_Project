def main():
    """
    Run the evennia launcher main program.

    """
    # set up argument parser

    parser = ArgumentParser(description=CMDLINE_HELP, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '--gamedir', nargs=1, action='store', dest='altgamedir',
        metavar="<path>",
        help="location of gamedir (default: current location)")
    parser.add_argument(
        '--init', action='store', dest="init", metavar="<gamename>",
        help="creates a new gamedir 'name' at current location")
    parser.add_argument(
        '--log', '-l', action='store_true', dest='tail_log', default=False,
        help="tail the portal and server logfiles and print to stdout")
    parser.add_argument(
        '--list', nargs='+', action='store', dest='listsetting', metavar="all|<key>",
        help=("list settings, use 'all' to list all available keys"))
    parser.add_argument(
        '--settings', nargs=1, action='store', dest='altsettings',
        default=None, metavar="<path>",
        help=("start evennia with alternative settings file from\n"
              " gamedir/server/conf/. (default is settings.py)"))
    parser.add_argument(
        '--initsettings', action='store_true', dest="initsettings",
        default=False,
        help="create a new, empty settings file as\n gamedir/server/conf/settings.py")
    parser.add_argument(
        '--initmissing', action='store_true', dest="initmissing",
        default=False,
        help="checks for missing secret_settings or server logs\n directory, and adds them if needed")
    parser.add_argument(
        '--profiler', action='store_true', dest='profiler', default=False,
        help="start given server component under the Python profiler")
    parser.add_argument(
        '--dummyrunner', nargs=1, action='store', dest='dummyrunner',
        metavar="<N>",
        help="test a server by connecting <N> dummy accounts to it")
    parser.add_argument(
        '-v', '--version', action='store_true',
        dest='show_version', default=False,
        help="show version info")

    parser.add_argument(
        "operation", nargs='?', default="noop",
        help=ARG_OPTIONS)
    parser.epilog = (
        "Common Django-admin commands are shell, dbshell, test and migrate.\n"
        "See the Django documentation for more management commands.")

    args, unknown_args = parser.parse_known_args()

    # handle arguments
    option = args.operation

    # make sure we have everything
    check_main_evennia_dependencies()

    if not args:
        # show help pane
        print(CMDLINE_HELP)
        sys.exit()

    if args.altgamedir:
        # use alternative gamedir path
        global GAMEDIR
        altgamedir = args.altgamedir[0]
        if not os.path.isdir(altgamedir) and not args.init:
            print(ERROR_NO_ALT_GAMEDIR.format(gamedir=altgamedir))
            sys.exit()
        GAMEDIR = altgamedir

    if args.init:
        # initialization of game directory
        create_game_directory(args.init)
        print(CREATED_NEW_GAMEDIR.format(
            gamedir=args.init,
            settings_path=os.path.join(args.init, SETTINGS_PATH)))
        sys.exit()

    if args.show_version:
        # show the version info
        print(show_version_info(option == "help"))
        sys.exit()

    if args.altsettings:
        # use alternative settings file
        global SETTINGSFILE, SETTINGS_DOTPATH, ENFORCED_SETTING
        sfile = args.altsettings[0]
        SETTINGSFILE = sfile
        ENFORCED_SETTING = True
        SETTINGS_DOTPATH = "server.conf.%s" % sfile.rstrip(".py")
        print("Using settings file '%s' (%s)." % (
            SETTINGSFILE, SETTINGS_DOTPATH))

    if args.initsettings:
        # create new settings file
        try:
            create_settings_file(init=False)
            print(RECREATED_SETTINGS)
        except IOError:
            print(ERROR_INITSETTINGS)
        sys.exit()

    if args.initmissing:
        try:
            log_path = os.path.join(SERVERDIR, "logs")
            if not os.path.exists(log_path):
                os.makedirs(log_path)

            settings_path = os.path.join(CONFDIR, "secret_settings.py")
            if not os.path.exists(settings_path):
                create_settings_file(init=False, secret_settings=True)

            print(RECREATED_MISSING)
        except IOError:
            print(ERROR_INITMISSING)
        sys.exit()

    if args.tail_log:
        # set up for tailing the log files
        global NO_REACTOR_STOP
        NO_REACTOR_STOP = True
        if not SERVER_LOGFILE:
            init_game_directory(CURRENT_DIR, check_db=False)

        # adjust how many lines we show from existing logs
        start_lines1, start_lines2 = 20, 20
        if option not in ('reload', 'reset', 'noop'):
            start_lines1, start_lines2 = 0, 0

        tail_log_files(PORTAL_LOGFILE, SERVER_LOGFILE, start_lines1, start_lines2)
        print("   Tailing logfiles {} (Ctrl-C to exit) ...".format(
            _file_names_compact(SERVER_LOGFILE, PORTAL_LOGFILE)))
    if args.dummyrunner:
        # launch the dummy runner
        init_game_directory(CURRENT_DIR, check_db=True)
        run_dummyrunner(args.dummyrunner[0])
    elif args.listsetting:
        # display all current server settings
        init_game_directory(CURRENT_DIR, check_db=False)
        list_settings(args.listsetting)
    elif option == 'menu':
        # launch menu for operation
        init_game_directory(CURRENT_DIR, check_db=True)
        run_menu()
    elif option in ('status', 'info', 'start', 'istart', 'ipstart', 'reload', 'restart', 'reboot',
                    'reset', 'stop', 'sstop', 'kill', 'skill', 'sstart'):
        # operate the server directly
        if not SERVER_LOGFILE:
            init_game_directory(CURRENT_DIR, check_db=True)
        if option == "status":
            query_status()
        elif option == "info":
            query_info()
        elif option == "start":
            start_evennia(args.profiler, args.profiler)
        elif option == "istart":
            start_server_interactive()
        elif option == "ipstart":
            start_portal_interactive()
        elif option in ('reload', 'restart'):
            reload_evennia(args.profiler)
        elif option == 'reboot':
            reboot_evennia(args.profiler, args.profiler)
        elif option == 'reset':
            reload_evennia(args.profiler, reset=True)
        elif option == 'stop':
            stop_evennia()
        elif option == 'sstop':
            stop_server_only()
        elif option == 'sstart':
            start_only_server()
        elif option == 'kill':
            if _is_windows():
                print("This option is not supported on Windows.")
            else:
                kill(SERVER_PIDFILE, 'Server')
                kill(PORTAL_PIDFILE, 'Portal')
        elif option == 'skill':
            if _is_windows():
                print("This option is not supported on Windows.")
            else:
                kill(SERVER_PIDFILE, 'Server')
    elif option != "noop":
        # pass-through to django manager, but set things up first
        check_db = False
        need_gamedir = True
        # some commands don't require the presence of a game directory to work
        if option in ('makemessages', 'compilemessages'):
            need_gamedir = False

        # handle special django commands
        if option in ('runserver', 'testserver'):
            print(WARNING_RUNSERVER)
        if option in ("shell", "check"):
            # some django commands requires the database to exist,
            # or evennia._init to have run before they work right.
            check_db = True
        if option == "test":
            global TEST_MODE
            TEST_MODE = True

        init_game_directory(CURRENT_DIR, check_db=check_db, need_gamedir=need_gamedir)

        if option == "migrate":
            # we have to launch migrate within the program to make sure migrations
            # run within the scope of the launcher (otherwise missing a db will cause errors)
            django.core.management.call_command(*([option] + unknown_args))
        else:
            # pass on to the core django manager - re-parse the entire input line
            # but keep 'evennia' as the name instead of django-admin. This is
            # an exit condition.
            sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
            sys.exit(execute_from_command_line())

    elif not args.tail_log:
        # no input; print evennia info (don't pring if we're tailing log)
        print(ABOUT_INFO)

    if REACTOR_RUN:
        reactor.run()