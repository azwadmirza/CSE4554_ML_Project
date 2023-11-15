def cmdline_handler(scriptname, argv):
    parser = argparse.ArgumentParser(
        prog="hy",
        usage=USAGE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG)
    parser.add_argument("-c", dest="command",
                        help="program passed in as a string")
    parser.add_argument("-m", dest="mod",
                        help="module to run, passed in as a string")
    parser.add_argument(
        "-i", dest="icommand",
        help="program passed in as a string, then stay in REPL")
    parser.add_argument("--spy", action="store_true",
                        help="print equivalent Python code before executing")

    parser.add_argument("-v", action="version", version=VERSION)

    parser.add_argument("--show-tracebacks", action="store_true",
                        help="show complete tracebacks for Hy exceptions")

    # this will contain the script/program name and any arguments for it.
    parser.add_argument('args', nargs=argparse.REMAINDER,
                        help=argparse.SUPPRESS)

    # stash the hy executable in case we need it later
    # mimics Python sys.executable
    hy.executable = argv[0]

    # need to split the args if using "-m"
    # all args after the MOD are sent to the module
    # in sys.argv
    module_args = []
    if "-m" in argv:
        mloc = argv.index("-m")
        if len(argv) > mloc+2:
            module_args = argv[mloc+2:]
            argv = argv[:mloc+2]

    options = parser.parse_args(argv[1:])

    if options.show_tracebacks:
        global SIMPLE_TRACEBACKS
        SIMPLE_TRACEBACKS = False

    # reset sys.argv like Python
    sys.argv = options.args + module_args or [""]

    if options.command:
        # User did "hy -c ..."
        return run_command(options.command)

    if options.mod:
        # User did "hy -m ..."
        return run_module(options.mod)

    if options.icommand:
        # User did "hy -i ..."
        return run_icommand(options.icommand, spy=options.spy)

    if options.args:
        if options.args[0] == "-":
            # Read the program from stdin
            return run_command(sys.stdin.read())

        else:
            # User did "hy <filename>"
            try:
                return run_file(options.args[0])
            except HyIOError as e:
                print("hy: Can't open file '{0}': [Errno {1}] {2}\n".format(
                    e.filename, e.errno, e.strerror), file=sys.stderr)
                sys.exit(e.errno)

    # User did NOTHING!
    return run_repl(spy=options.spy)