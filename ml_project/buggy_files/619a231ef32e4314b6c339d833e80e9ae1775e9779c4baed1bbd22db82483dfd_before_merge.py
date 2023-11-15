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
    parser.add_argument("-E", action='store_true',
                        help="ignore PYTHON* environment variables")
    parser.add_argument("-B", action='store_true',
                        help="don't write .py[co] files on import; also PYTHONDONTWRITEBYTECODE=x")
    parser.add_argument("-i", dest="icommand",
                        help="program passed in as a string, then stay in REPL")
    parser.add_argument("--spy", action="store_true",
                        help="print equivalent Python code before executing")
    parser.add_argument("--repl-output-fn",
                        help="function for printing REPL output "
                             "(e.g., hy.contrib.hy-repr.hy-repr)")
    parser.add_argument("-v", "--version", action="version", version=VERSION)

    # this will contain the script/program name and any arguments for it.
    parser.add_argument('args', nargs=argparse.REMAINDER,
                        help=argparse.SUPPRESS)

    # Get the path of the Hy cmdline executable and swap it with
    # `sys.executable` (saving the original, just in case).
    # XXX: The `__main__` module will also have `__file__` set to the
    # entry-point script.  Currently, I don't see an immediate problem, but
    # that's not how the Python cmdline works.
    hy.executable = argv[0]
    hy.sys_executable = sys.executable
    sys.executable = hy.executable

    # Need to split the args.  If using "-m" all args after the MOD are sent to
    # the module in sys.argv.
    module_args = []
    if "-m" in argv:
        mloc = argv.index("-m")
        if len(argv) > mloc+2:
            module_args = argv[mloc+2:]
            argv = argv[:mloc+2]

    options = parser.parse_args(argv[1:])

    if options.E:
        # User did "hy -E ..."
        _remove_python_envs()

    if options.B:
        sys.dont_write_bytecode = True

    if options.command:
        # User did "hy -c ..."
        return run_command(options.command, filename='<string>')

    if options.mod:
        # User did "hy -m ..."
        sys.argv = [sys.argv[0]] + options.args + module_args
        runpy.run_module(options.mod, run_name='__main__', alter_sys=True)
        return 0

    if options.icommand:
        # User did "hy -i ..."
        return run_icommand(options.icommand, spy=options.spy,
                            output_fn=options.repl_output_fn)

    if options.args:
        if options.args[0] == "-":
            # Read the program from stdin
            return run_command(sys.stdin.read(), filename='<stdin>')

        else:
            # User did "hy <filename>"
            filename = options.args[0]

            # Emulate Python cmdline behavior by setting `sys.path` relative
            # to the executed file's location.
            if sys.path[0] == '':
                sys.path[0] = os.path.realpath(os.path.split(filename)[0])
            else:
                sys.path.insert(0, os.path.split(filename)[0])

            try:
                sys.argv = options.args
                with filtered_hy_exceptions():
                    runhy.run_path(filename, run_name='__main__')
                return 0
            except FileNotFoundError as e:
                print("hy: Can't open file '{0}': [Errno {1}] {2}".format(
                      e.filename, e.errno, e.strerror), file=sys.stderr)
                sys.exit(e.errno)

    # User did NOTHING!
    return run_repl(spy=options.spy, output_fn=options.repl_output_fn)