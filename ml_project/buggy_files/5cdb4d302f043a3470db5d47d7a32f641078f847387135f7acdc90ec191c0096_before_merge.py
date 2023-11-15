def main(subcommands=None):
    """
    CodeChecker main command line.
    """

    def signal_handler(signum, frame):
        """
        Without this handler the PostgreSQL
        server does not terminate at signal.
        """
        sys.exit(128 + signum)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        parser = argparse.ArgumentParser(
            prog="CodeChecker",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="""Run the CodeChecker sourcecode analyzer framework.
Please specify a subcommand to access individual features.""",
            epilog="""Example scenario: Analyzing, and storing results
------------------------------------------------
Start the server where the results will be stored and can be viewed
after the analysis is done:
    CodeChecker server

Analyze a project with default settings:
    CodeChecker check -b "cd ~/myproject && make" -o "~/results"

Store the analyzer results to the server:
    CodeChecker store "~/results" -n myproject

The results can be viewed:
 * In a web browser: http://localhost:8001
 * In the command line:
    CodeChecker cmd results myproject

Example scenario: Analyzing, and printing results to Terminal (no storage)
--------------------------------------------------------------------------
In this case, no database is used, and the results are printed on the standard
output.

    CodeChecker check -b "cd ~/myproject && make\" """)

        subparsers = parser.add_subparsers(help='commands')

        if subcommands:
            # Try to check if the user has already given us a subcommand to
            # execute. If so, don't load every available parts of CodeChecker
            # to ensure a more optimised run.
            if len(sys.argv) > 1:
                first_command = sys.argv[1]
                if first_command in subcommands:

                    # Consider only the given command as an available one.
                    subcommands = {first_command: subcommands[first_command]}

            for subcommand in subcommands:
                try:
                    add_subcommand(subparsers, subcommand,
                                   subcommands[subcommand])
                except (IOError, ImportError):
                    print("Couldn't import module for subcommand '" +
                          subcommand + "'... ignoring.")
                    import traceback
                    traceback.print_exc(file=sys.stdout)

        args = parser.parse_args()

        # Call handler function to process configuration files. If there are
        # any configuration options available in one of the given file than
        # extend the system argument list with these options and try to parse
        # the argument list again to validate it.
        if 'func_process_config_file' in args:
            cfg_args = args.func_process_config_file(args)
            if cfg_args:
                sys.argv.extend(cfg_args)
                args = parser.parse_args()

        args.func(args)

    except KeyboardInterrupt as kb_err:
        print(str(kb_err))
        print("Interrupted by user...")
        sys.exit(1)

    # Handle all exception, but print stacktrace. It is needed for atexit.
    # atexit does not work correctly when an unhandled exception occurred.
    # So in this case, the servers left running when the script exited.
    except Exception:
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)