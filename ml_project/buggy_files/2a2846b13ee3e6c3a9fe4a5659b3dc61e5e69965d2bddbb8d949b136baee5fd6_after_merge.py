def add_arguments_to_parser(parser):
    """
    Add the subcommand's arguments to the given argparse.ArgumentParser.
    """

    default_workspace = env.get_default_workspace()

    # TODO: --workspace is an outdated concept in 'store'. Later on,
    # it shall be deprecated, as changes to db_handler commence.
    parser.add_argument('-w', '--workspace',
                        type=str,
                        dest="workspace",
                        default=default_workspace,
                        required=False,
                        help="Directory where CodeChecker can store analysis "
                             "result related data, such as the database. "
                             "(Cannot be specified at the same time with "
                             "'--sqlite' or '--config-directory'.)")

    parser.add_argument('-f', '--config-directory',
                        type=str,
                        dest="config_directory",
                        default=default_workspace,
                        required=False,
                        help="Directory where CodeChecker server should read "
                             "server-specific configuration (such as "
                             "authentication settings, SSL certificate"
                             " (cert.pem) and key (key.pem)) from.")

    parser.add_argument('--host',
                        type=str,
                        dest="listen_address",
                        default="localhost",
                        required=False,
                        help="The IP address or hostname of the server on "
                             "which it should listen for connections.")

    # TODO: -v/--view-port is too verbose. The server's -p/--port is used
    # symmetrically in 'CodeChecker cmd' anyways.
    parser.add_argument('-v', '--view-port',  # TODO: <- Deprecate and remove.
                        '-p', '--port',
                        type=int,
                        dest="view_port",
                        metavar='PORT',
                        default=8001,
                        required=False,
                        help="The port which will be used as listen port for "
                             "the server.")

    # TODO: This should be removed later on, in favour of --host.
    parser.add_argument('--not-host-only',
                        dest="not_host_only",
                        action="store_true",
                        required=False,
                        help="If specified, storing and viewing the results "
                             "will be possible not only by browsers and "
                             "clients running locally, but to everyone, who "
                             "can access the server over the Internet. "
                             "(Equivalent to specifying '--host \"\"'.)")

    parser.add_argument('--skip-db-cleanup',
                        dest="skip_db_cleanup",
                        action='store_true',
                        default=False,
                        required=False,
                        help="Skip performing cleanup jobs on the database "
                             "like removing unused files.")

    dbmodes = parser.add_argument_group("configuration database arguments")

    dbmodes = dbmodes.add_mutually_exclusive_group(required=False)

    dbmodes.add_argument('--sqlite',
                         type=str,
                         dest="sqlite",
                         metavar='SQLITE_FILE',
                         default=os.path.join(
                             '<CONFIG_DIRECTORY>',
                             "config.sqlite"),
                         required=False,
                         help="Path of the SQLite database file to use.")

    dbmodes.add_argument('--postgresql',
                         dest="postgresql",
                         action='store_true',
                         required=False,
                         default=argparse.SUPPRESS,
                         help="Specifies that a PostgreSQL database is to be "
                              "used instead of SQLite. See the \"PostgreSQL "
                              "arguments\" section on how to configure the "
                              "database connection.")

    pgsql = parser.add_argument_group("PostgreSQL arguments",
                                      "Values of these arguments are ignored, "
                                      "unless '--postgresql' is specified!")

    # TODO: --dbSOMETHING arguments are kept to not break interface from
    # old command. Database using commands such as "CodeChecker store" no
    # longer supports these --- it would be ideal to break and remove args
    # with this style and only keep --db-SOMETHING.
    pgsql.add_argument('--dbaddress', '--db-host',
                       type=str,
                       dest="dbaddress",
                       default="localhost",
                       required=False,
                       help="Database server address.")

    pgsql.add_argument('--dbport', '--db-port',
                       type=int,
                       dest="dbport",
                       default=5432,
                       required=False,
                       help="Database server port.")

    pgsql.add_argument('--dbusername', '--db-username',
                       type=str,
                       dest="dbusername",
                       default='codechecker',
                       required=False,
                       help="Username to use for connection.")

    pgsql.add_argument('--dbname', '--db-name',
                       type=str,
                       dest="dbname",
                       default="config",
                       required=False,
                       help="Name of the database to use.")

    root_account = parser.add_argument_group(
        "root account arguments",
        "Servers automatically create a root user to access the server's "
        "configuration via the clients. This user is created at first start "
        "and saved in the CONFIG_DIRECTORY, and the credentials are printed "
        "to the server's standard output. The plaintext credentials are "
        "NEVER accessible again.")

    root_account.add_argument('--reset-root',
                              dest="reset_root",
                              action='store_true',
                              default=argparse.SUPPRESS,
                              required=False,
                              help="Force the server to recreate the master "
                                   "superuser (root) account name and "
                                   "password. The previous credentials will "
                                   "be invalidated, and the new ones will be "
                                   "printed to the standard output.")

    root_account.add_argument('--force-authentication',
                              dest="force_auth",
                              action='store_true',
                              default=argparse.SUPPRESS,
                              required=False,
                              help="Force the server to run in "
                                   "authentication requiring mode, despite "
                                   "the configuration value in "
                                   "'server_config.json'. This is needed "
                                   "if you need to edit the product "
                                   "configuration of a server that would not "
                                   "require authentication otherwise.")

    instance_mgmnt = parser.add_argument_group("running server management")

    instance_mgmnt = instance_mgmnt. \
        add_mutually_exclusive_group(required=False)

    instance_mgmnt.add_argument('-l', '--list',
                                dest="list",
                                action='store_true',
                                default=argparse.SUPPRESS,
                                required=False,
                                help="List the servers that has been started "
                                     "by you.")

    instance_mgmnt.add_argument('-r', '--reload',
                                dest="reload",
                                action='store_true',
                                default=argparse.SUPPRESS,
                                required=False,
                                help="Sends the CodeChecker server process a "
                                     "SIGHUP signal, causing it to reread "
                                     "it's configuration files.")

    # TODO: '-s' was removed from 'quickcheck', it shouldn't be here either?
    instance_mgmnt.add_argument('-s', '--stop',
                                dest="stop",
                                action='store_true',
                                default=argparse.SUPPRESS,
                                required=False,
                                help="Stops the server associated with "
                                     "the given view-port and workspace.")

    instance_mgmnt.add_argument('--stop-all',
                                dest="stop_all",
                                action='store_true',
                                default=argparse.SUPPRESS,
                                required=False,
                                help="Stops all of your running CodeChecker "
                                     "server instances.")

    database_mgmnt = parser.add_argument_group(
            "Database management arguments.",
            """WARNING these commands needs to be called with the same
            workspace and configuration arguments as the server so the
            configuration database will be found which is required for the
            schema migration. Migration can be done without a running server
            but pay attention to use the same arguments which will be used to
            start the server.
            NOTE:
            Before migration it is advised to create a full a backup of
            the product databases.
            """)

    database_mgmnt = database_mgmnt. \
        add_mutually_exclusive_group(required=False)

    database_mgmnt.add_argument('--db-status',
                                type=str,
                                dest="status",
                                action='store',
                                default=argparse.SUPPRESS,
                                required=False,
                                help="Name of the product to get "
                                     "the database status for. "
                                     "Use 'all' to list the database "
                                     "statuses for all of the products.")

    database_mgmnt.add_argument('--db-upgrade-schema',
                                type=str,
                                dest='product_to_upgrade',
                                action='store',
                                default=argparse.SUPPRESS,
                                required=False,
                                help="Name of the product to upgrade to the "
                                     "latest database schema available in "
                                     "the package. Use 'all' to upgrade all "
                                     "of the products. "
                                     "NOTE: Before migration it is advised"
                                     " to create a full backup of "
                                     "the product databases.")

    database_mgmnt.add_argument('--db-force-upgrade',
                                dest='force_upgrade',
                                action='store_true',
                                default=argparse.SUPPRESS,
                                required=False,
                                help="Force the server to do database "
                                     "migration without user interaction. "
                                     "NOTE: Please use with caution and "
                                     "before automatic migration it is "
                                     "advised to create a full backup of the "
                                     "product databases.")

    logger.add_verbose_arguments(parser)

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

    parser.set_defaults(func=__handle)