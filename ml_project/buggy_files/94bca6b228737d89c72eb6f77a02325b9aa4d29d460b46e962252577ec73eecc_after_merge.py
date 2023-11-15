def parse_args(args):
    p = DBTArgumentParser(
        prog='dbt: data build tool',
        formatter_class=argparse.RawTextHelpFormatter,
        description="An ELT tool for managing your SQL "
        "transformations and data models."
        "\nFor more documentation on these commands, visit: "
        "docs.getdbt.com",
        epilog="Specify one of these sub-commands and you can "
        "find more help from there.")

    p.add_argument(
        '--version',
        action='dbtversion',
        help="Show version information")

    p.add_argument(
        '-r',
        '--record-timing-info',
        default=None,
        type=str,
        help="""
        When this option is passed, dbt will output low-level timing
        stats to the specified file. Example:
        `--record-timing-info output.profile`
        """
    )

    p.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='''Display debug logging during dbt execution. Useful for
        debugging and making bug reports.''')

    p.add_argument(
        '-S',
        '--strict',
        action='store_true',
        help='''Run schema validations at runtime. This will surface
        bugs in dbt, but may incur a performance penalty.''')

    # if set, run dbt in single-threaded mode: thread count is ignored, and
    # calls go through `map` instead of the thread pool. This is useful for
    # getting performance information about aspects of dbt that normally run in
    # a thread, as the profiler ignores child threads. Users should really
    # never use this.
    p.add_argument(
        '--single-threaded',
        action='store_true',
        help=argparse.SUPPRESS,
    )

    subs = p.add_subparsers(title="Available sub-commands")

    base_subparser = argparse.ArgumentParser(add_help=False)

    base_subparser.add_argument(
        '--profiles-dir',
        default=PROFILES_DIR,
        type=str,
        help="""
        Which directory to look in for the profiles.yml file. Default = {}
        """.format(PROFILES_DIR)
    )

    base_subparser.add_argument(
        '--profile',
        required=False,
        type=str,
        help="""
        Which profile to load. Overrides setting in dbt_project.yml.
        """
    )

    base_subparser.add_argument(
        '--target',
        default=None,
        type=str,
        help='Which target to load for the given profile'
    )

    base_subparser.add_argument(
        '--vars',
        type=str,
        default='{}',
        help="""
            Supply variables to the project. This argument overrides
            variables defined in your dbt_project.yml file. This argument
            should be a YAML string, eg. '{my_variable: my_value}'"""
    )

    # if set, log all cache events. This is extremely verbose!
    base_subparser.add_argument(
        '--log-cache-events',
        action='store_true',
        help=argparse.SUPPRESS,
    )

    base_subparser.add_argument(
        '--bypass-cache',
        action='store_false',
        dest='use_cache',
        help='If set, bypass the adapter-level cache of database state',
    )

    sub = subs.add_parser(
            'init',
            parents=[base_subparser],
            help="Initialize a new DBT project.")
    sub.add_argument('project_name', type=str, help='Name of the new project')
    sub.set_defaults(cls=init_task.InitTask, which='init')

    sub = subs.add_parser(
        'clean',
        parents=[base_subparser],
        help="Delete all folders in the clean-targets list"
        "\n(usually the dbt_modules and target directories.)")
    sub.set_defaults(cls=clean_task.CleanTask, which='clean')

    sub = subs.add_parser(
        'debug',
        parents=[base_subparser],
        help="Show some helpful information about dbt for debugging."
        "\nNot to be confused with the --debug option which increases "
        "verbosity.")
    sub.add_argument(
        '--config-dir',
        action='store_true',
        help="""
        If specified, DBT will show path information for this project
        """
    )
    sub.set_defaults(cls=debug_task.DebugTask, which='debug')

    sub = subs.add_parser(
        'deps',
        parents=[base_subparser],
        help="Pull the most recent version of the dependencies "
        "listed in packages.yml")
    sub.set_defaults(cls=deps_task.DepsTask, which='deps')

    sub = subs.add_parser(
        'archive',
        parents=[base_subparser],
        help="Record changes to a mutable table over time."
             "\nMust be configured in your dbt_project.yml.")
    sub.add_argument(
        '--threads',
        type=int,
        required=False,
        help="""
        Specify number of threads to use while archiving tables. Overrides
        settings in profiles.yml.
        """
    )
    sub.set_defaults(cls=archive_task.ArchiveTask, which='archive')

    run_sub = subs.add_parser(
        'run',
        parents=[base_subparser],
        help="Compile SQL and execute against the current "
        "target database.")
    run_sub.set_defaults(cls=run_task.RunTask, which='run')

    compile_sub = subs.add_parser(
        'compile',
        parents=[base_subparser],
        help="Generates executable SQL from source model, test, and"
        "analysis files. \nCompiled SQL files are written to the target/"
        "directory.")
    compile_sub.set_defaults(cls=compile_task.CompileTask, which='compile')

    docs_sub = subs.add_parser(
        'docs',
        parents=[base_subparser],
        help="Generate or serve the documentation "
        "website for your project.")
    docs_subs = docs_sub.add_subparsers()
    # it might look like docs_sub is the correct parents entry, but that
    # will cause weird errors about 'conflicting option strings'.
    generate_sub = docs_subs.add_parser('generate', parents=[base_subparser])
    generate_sub.set_defaults(cls=generate_task.GenerateTask,
                              which='generate')
    generate_sub.add_argument(
        '--no-compile',
        action='store_false',
        dest='compile',
        help='Do not run "dbt compile" as part of docs generation'
    )

    for sub in [run_sub, compile_sub, generate_sub]:
        sub.add_argument(
            '-m',
            '--models',
            required=False,
            nargs='+',
            help="""
            Specify the models to include.
            """
        )
        sub.add_argument(
            '--exclude',
            required=False,
            nargs='+',
            help="""
            Specify the models to exclude.
            """
        )
        sub.add_argument(
            '--threads',
            type=int,
            required=False,
            help="""
            Specify number of threads to use while executing models. Overrides
            settings in profiles.yml.
            """
        )
        sub.add_argument(
            '--non-destructive',
            action='store_true',
            help="""
            If specified, DBT will not drop views. Tables will be truncated
            instead of dropped.
            """
        )
        sub.add_argument(
            '--full-refresh',
            action='store_true',
            help="""
            If specified, DBT will drop incremental models and
            fully-recalculate the incremental table from the model definition.
            """)

    seed_sub = subs.add_parser(
        'seed',
        parents=[base_subparser],
        help="Load data from csv files into your data warehouse.")
    seed_sub.add_argument(
        '--drop-existing',
        action='store_true',
        help='(DEPRECATED) Use --full-refresh instead.'
    )
    seed_sub.add_argument(
        '--full-refresh',
        action='store_true',
        help='Drop existing seed tables and recreate them'
    )
    seed_sub.add_argument(
        '--show',
        action='store_true',
        help='Show a sample of the loaded data in the terminal'
    )
    seed_sub.set_defaults(cls=seed_task.SeedTask, which='seed')

    serve_sub = docs_subs.add_parser('serve', parents=[base_subparser])
    serve_sub.add_argument(
        '--port',
        default=8080,
        type=int,
        help='Specify the port number for the docs server.'
    )
    serve_sub.set_defaults(cls=serve_task.ServeTask,
                           which='serve')

    sub = subs.add_parser(
        'test',
        parents=[base_subparser],
        help="Runs tests on data in deployed models."
        "Run this after `dbt run`")
    sub.add_argument(
        '--data',
        action='store_true',
        help='Run data tests defined in "tests" directory.'
    )
    sub.add_argument(
        '--schema',
        action='store_true',
        help='Run constraint validations from schema.yml files'
    )
    sub.add_argument(
        '--threads',
        type=int,
        required=False,
        help="""
        Specify number of threads to use while executing tests. Overrides
        settings in profiles.yml
        """
    )
    sub.add_argument(
        '-m',
        '--models',
        required=False,
        nargs='+',
        help="""
        Specify the models to test.
        """
    )
    sub.add_argument(
        '--exclude',
        required=False,
        nargs='+',
        help="""
        Specify the models to exclude from testing.
        """
    )

    sub.set_defaults(cls=test_task.TestTask, which='test')

    if len(args) == 0:
        p.print_help()
        sys.exit(1)

    parsed = p.parse_args(args)
    parsed.profiles_dir = os.path.expanduser(parsed.profiles_dir)

    if not hasattr(parsed, 'which'):
        # the user did not provide a valid subcommand. trigger the help message
        # and exit with a error
        p.print_help()
        p.exit(1)

    return parsed