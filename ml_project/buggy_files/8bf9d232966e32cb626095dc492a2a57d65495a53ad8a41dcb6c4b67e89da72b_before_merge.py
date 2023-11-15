def main():
    """
    Run the evennia launcher main program.

    """

    # set up argument parser

    parser = ArgumentParser(description=CMDLINE_HELP)
    parser.add_argument(
        '-v', '--version', action='store_true',
        dest='show_version', default=False,
        help="Show version info.")
    parser.add_argument(
        '-i', '--interactive', action='store_true',
        dest='interactive', default=False,
        help="Start given processes in interactive mode.")
    parser.add_argument(
        '-l', '--log', action='store_true',
        dest="logserver", default=False,
        help="Log Server data to log file.")
    parser.add_argument(
        '--init', action='store', dest="init", metavar="name",
        help="Creates a new game directory 'name' at the current location.")
    parser.add_argument(
        '--list', nargs='+', action='store', dest='listsetting', metavar="key",
        help=("List values for server settings. Use 'all' to list all "
              "available keys."))
    parser.add_argument(
        '--profiler', action='store_true', dest='profiler', default=False,
        help="Start given server component under the Python profiler.")
    parser.add_argument(
        '--dummyrunner', nargs=1, action='store', dest='dummyrunner',
        metavar="N",
        help="Test a running server by connecting N dummy accounts to it.")
    parser.add_argument(
        '--settings', nargs=1, action='store', dest='altsettings',
        default=None, metavar="filename.py",
        help=("Start evennia with alternative settings file from "
              "gamedir/server/conf/. (default is settings.py)"))
    parser.add_argument(
        '--initsettings', action='store_true', dest="initsettings",
        default=False,
        help="Create a new, empty settings file as gamedir/server/conf/settings.py.")
    parser.add_argument(
        '--external-runner', action='store_true', dest="doexit",
        default=False,
        help="Handle server restart with an external process manager.")
    parser.add_argument(
        "operation", nargs='?', default="noop",
        help="Operation to perform: 'start', 'stop', 'reload' or 'menu'.")
    parser.add_argument(
        "service", metavar="component", nargs='?', default="all",
        help=("Which component to operate on: "
              "'server', 'portal' or 'all' (default if not set)."))
    parser.epilog = (
        "Common usage: evennia start|stop|reload. Django-admin database commands:"
        "evennia migration|flush|shell|dbshell (see the django documentation for more django-admin commands.)")

    args, unknown_args = parser.parse_known_args()

    # handle arguments
    option, service = args.operation, args.service

    # make sure we have everything
    check_main_evennia_dependencies()

    if not args:
        # show help pane
        print(CMDLINE_HELP)
        sys.exit()
    elif args.init:
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
        sfile = args.altsettings[0]
        global SETTINGSFILE, SETTINGS_DOTPATH, ENFORCED_SETTING
        SETTINGSFILE = sfile
        ENFORCED_SETTING = True
        SETTINGS_DOTPATH = "server.conf.%s" % sfile.rstrip(".py")
        print("Using settings file '%s' (%s)." % (
            SETTINGSFILE, SETTINGS_DOTPATH))

    if args.initsettings:
        # create new settings file
        global GAMEDIR
        GAMEDIR = os.getcwd()
        try:
            create_settings_file(init=False)
            print(RECREATED_SETTINGS)
        except IOError:
            print(ERROR_INITSETTINGS)
        sys.exit()

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
    elif option in ('start', 'reload', 'stop'):
        # operate the server directly
        init_game_directory(CURRENT_DIR, check_db=True)
        server_operation(option, service, args.interactive, args.profiler, args.logserver, doexit=args.doexit)
    elif option != "noop":
        # pass-through to django manager
        check_db = False
        if option in ('runserver', 'testserver'):
            print(WARNING_RUNSERVER)
        if option == "shell":
            # to use the shell we need to initialize it first,
            # and this only works if the database is set up
            check_db = True
        if option == "test":
            global TEST_MODE
            TEST_MODE = True
        init_game_directory(CURRENT_DIR, check_db=check_db)

        args = [option]
        kwargs = {}
        if service not in ("all", "server", "portal"):
            args.append(service)
        if unknown_args:
            for arg in unknown_args:
                if arg.startswith("--"):
                    print("arg:", arg)
                    if "=" in arg:
                        arg, value = [p.strip() for p in arg.split("=", 1)]
                    else:
                        value = True
                    kwargs[arg.lstrip("--")] = value
                else:
                    args.append(arg)
        try:
            django.core.management.call_command(*args, **kwargs)
        except django.core.management.base.CommandError as exc:
            args = ", ".join(args)
            kwargs = ", ".join(["--%s" % kw for kw in kwargs])
            print(ERROR_INPUT.format(traceback=exc, args=args, kwargs=kwargs))
    else:
        # no input; print evennia info
        print(ABOUT_INFO)