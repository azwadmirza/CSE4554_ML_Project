def main():
    """"Initialize settings (not implemented) and create main window/application."""

    parser = argparse.ArgumentParser(description = 'OpenShot version ' + info.SETUP['version'])
    parser.add_argument('-l', '--lang', action='store',
        help='language code for interface (overrides '
             'preferences and system environment)')
    parser.add_argument('--list-languages', dest='list_languages',
        action='store_true',
        help='List all language codes supported by OpenShot')
    parser.add_argument('--path', dest='py_path', action='append',
        help='Additional locations to search for modules '
              '(PYTHONPATH). Can be used multiple times.')
    parser.add_argument('--test-models', dest='modeltest',
       action='store_true',
       help="Load Qt's QAbstractItemModelTester into data models "
       '(requires Qt 5.11+)')
    parser.add_argument('-d', '--debug', action='store_true',
        help='Enable debugging output')
    parser.add_argument('--debug-file', action='store_true',
        help='Debugging output (logfile only)')
    parser.add_argument('--debug-console', action='store_true',
        help='Debugging output (console only)')
    parser.add_argument('-V', '--version', action='store_true')
    parser.add_argument('remain', nargs=argparse.REMAINDER,
       help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Display version and exit (if requested)
    if args.version:
        print("OpenShot version %s" % info.SETUP['version'])
        sys.exit()

    # Set up debugging log level to requested streams
    if args.debug or args.debug_file:
            info.LOG_LEVEL_FILE = 'DEBUG'
    if args.debug or args.debug_console:
            info.LOG_LEVEL_CONSOLE = 'DEBUG'

    if args.list_languages:
        from classes.language import get_all_languages
        print("Supported Languages:")
        for lang in get_all_languages():
            print("  {:>12}  {}".format(lang[0],lang[1]))
        sys.exit()

    if args.py_path:
        for p in args.py_path:
            try:
                if os.path.exists(os.path.realpath(p)):
                    sys.path.insert(0, os.path.realpath(p))
                    print("Added {} to PYTHONPATH".format(os.path.realpath(p)))
                else:
                    print("{} does not exist".format(os.path.realpath(p)))
            except TypeError as ex:
                    print("Bad path {}: {}".format(p, ex))
                    continue

    if args.modeltest:
        info.MODEL_TEST = True
        # Set default logging rules, if the user didn't
        if os.getenv('QT_LOGGING_RULES') is None:
            os.putenv('QT_LOGGING_RULES', 'qt.modeltest.debug=true')

    if args.lang:
        if args.lang in info.SUPPORTED_LANGUAGES:
            info.CMDLINE_LANGUAGE = args.lang
        else:
            print("Unsupported language '{}'! (See --list-languages)".format(args.lang))
            sys.exit(-1)

    # Normal startup, print module path and lauch application
    print("Loaded modules from: %s" % info.PATH)

    # Create Qt application, pass any unprocessed arguments
    from classes.app import OpenShotApp

    argv = [sys.argv[0]]
    for arg in args.remain:
        argv.append(arg)
    app = OpenShotApp(argv)

    # Run and return result
    sys.exit(app.run())