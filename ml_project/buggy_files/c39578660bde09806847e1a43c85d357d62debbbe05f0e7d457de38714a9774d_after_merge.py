    def __handle(args):
        """Custom handler for 'server' so custom error messages can be
        printed without having to capture 'parser' in main."""

        def arg_match(options):
            return util.arg_match(options, sys.argv[1:])

        # See if there is a "PostgreSQL argument" specified in the invocation
        # without '--postgresql' being there. There is no way to distinguish
        # a default argument and a deliberately specified argument without
        # inspecting sys.argv.
        options = ['--dbaddress', '--dbport', '--dbusername', '--dbname',
                   '--db-host', '--db-port', '--db-username', '--db-name']
        psql_args_matching = arg_match(options)
        if any(psql_args_matching) and\
                'postgresql' not in args:
            first_matching_arg = next(iter([match for match
                                            in psql_args_matching]))
            parser.error("argument {0}: not allowed without "
                         "argument --postgresql".format(first_matching_arg))
            # parser.error() terminates with return code 2.

        # --not-host-only is a "shortcut", actually a to-be-deprecated
        # call which means '--host ""'.
        # TODO: Actually deprecate --not-host-only later on.
        options = ['--not-host-only', '--host']
        if set(arg_match(options)) == set(options):
            parser.error("argument --not-host-only: not allowed with "
                         "argument --host, as it is a shortcut to --host "
                         "\"\"")
        else:
            # Apply the shortcut.
            if arg_match(['--not-host-only']):
                args.listen_address = ""  # Listen on every interface.

            # --not-host-only is just a shortcut optstring, no actual use
            # is intended later on.
            delattr(args, 'not_host_only')

        # --workspace and --sqlite cannot be specified either, as
        # both point to a database location.
        options = ['--sqlite', '--workspace']
        options_short = ['--sqlite', '-w']
        if set(arg_match(options)) == set(options) or \
                set(arg_match(options_short)) == set(options_short):
            parser.error("argument --sqlite: not allowed with "
                         "argument --workspace")

        # --workspace and --config-directory also aren't allowed together now,
        # the latter one is expected to replace the earlier.
        options = ['--config-directory', '--workspace']
        options_short = ['--config-directory', '-w']
        if set(arg_match(options)) == set(options) or \
                set(arg_match(options_short)) == set(options_short):
            parser.error("argument --config-directory: not allowed with "
                         "argument --workspace")

        # If workspace is specified, sqlite is workspace/config.sqlite
        # and config_directory is the workspace directory.
        if arg_match(['--workspace', '-w']):
            args.config_directory = args.workspace
            args.sqlite = os.path.join(args.workspace,
                                       'config.sqlite')
            setattr(args, 'dbdatadir', os.path.join(args.workspace,
                                                    'pgsql_data'))

        # Workspace should not exist as a Namespace key.
        delattr(args, 'workspace')

        if '<CONFIG_DIRECTORY>' in args.sqlite:
            # Replace the placeholder variable with the actual value.
            args.sqlite = args.sqlite.replace('<CONFIG_DIRECTORY>',
                                              args.config_directory)

        # Convert relative sqlite file path to absolute.
        if 'sqlite' in args:
            args.sqlite = os.path.abspath(args.sqlite)

        if 'postgresql' not in args:
            # Later called database modules need the argument to be actually
            # present, even though the default is suppressed in the optstring.
            setattr(args, 'postgresql', False)

            # This is not needed by the database starter as we are
            # running SQLite.
            if 'dbdatadir' in args:
                delattr(args, 'dbdatadir')
        else:
            # If --postgresql is given, --sqlite is useless.
            delattr(args, 'sqlite')

        # If everything is fine, do call the handler for the subcommand.
        main(args)