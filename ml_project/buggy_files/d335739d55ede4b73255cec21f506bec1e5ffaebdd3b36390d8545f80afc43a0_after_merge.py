def parse_args(args):
    p = DBTArgumentParser(
        prog='dbt',
        description='''
        An ELT tool for managing your SQL transformations and data models.
        For more documentation on these commands, visit: docs.getdbt.com
        ''',
        epilog='''
        Specify one of these sub-commands and you can find more help from
        there.
        '''
    )

    p.add_argument(
        '--version',
        action='dbtversion',
        help='''
        Show version information
        ''')

    p.add_argument(
        '-r',
        '--record-timing-info',
        default=None,
        type=str,
        help='''
        When this option is passed, dbt will output low-level timing stats to
        the specified file. Example: `--record-timing-info output.profile`
        '''
    )

    p.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='''
        Display debug logging during dbt execution. Useful for debugging and
        making bug reports.
        '''
    )

    p.add_argument(
        '--no-write-json',
        action='store_false',
        dest='write_json',
        help='''
        If set, skip writing the manifest and run_results.json files to disk
        '''
    )

    p.add_argument(
        '-S',
        '--strict',
        action='store_true',
        help='''
        Run schema validations at runtime. This will surface bugs in dbt, but
        may incur a performance penalty.
        '''
    )

    p.add_argument(
        '--warn-error',
        action='store_true',
        help='''
        If dbt would normally warn, instead raise an exception. Examples
        include --models that selects nothing, deprecations, configurations
        with no associated models, invalid test configurations, and missing
        sources/refs in tests.
        '''
    )

    p.add_argument(
        '--partial-parse',
        action='store_true',
        help='''
        Allow for partial parsing by looking for and writing to a pickle file
        in the target directory.

        WARNING: This can result in unexpected behavior if you use env_var()!
        '''
    )

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

    # if set, extract all models and blocks with the jinja block extractor, and
    # verify that we don't fail anywhere the actual jinja parser passes. The
    # reverse (passing files that ends up failing jinja) is fine.
    p.add_argument(
        '--test-new-parser',
        action='store_true',
        help=argparse.SUPPRESS
    )

    subs = p.add_subparsers(title="Available sub-commands")

    base_subparser = _build_base_subparser()

    # make the subcommands that have their own subcommands
    docs_sub = _build_docs_subparser(subs, base_subparser)
    docs_subs = docs_sub.add_subparsers(title="Available sub-commands")
    source_sub = _build_source_subparser(subs, base_subparser)
    source_subs = source_sub.add_subparsers(title="Available sub-commands")

    _build_init_subparser(subs, base_subparser)
    _build_clean_subparser(subs, base_subparser)
    _build_debug_subparser(subs, base_subparser)
    _build_deps_subparser(subs, base_subparser)
    _build_list_subparser(subs, base_subparser)

    snapshot_sub = _build_snapshot_subparser(subs, base_subparser)
    rpc_sub = _build_rpc_subparser(subs, base_subparser)
    run_sub = _build_run_subparser(subs, base_subparser)
    compile_sub = _build_compile_subparser(subs, base_subparser)
    generate_sub = _build_docs_generate_subparser(docs_subs, base_subparser)
    test_sub = _build_test_subparser(subs, base_subparser)
    seed_sub = _build_seed_subparser(subs, base_subparser)
    # --threads, --no-version-check
    _add_common_arguments(run_sub, compile_sub, generate_sub, test_sub,
                          rpc_sub, seed_sub)
    # --models, --exclude
    _add_selection_arguments(run_sub, compile_sub, generate_sub, test_sub)
    _add_selection_arguments(snapshot_sub, models_name='select')
    # --full-refresh
    _add_table_mutability_arguments(run_sub, compile_sub)

    _build_docs_serve_subparser(docs_subs, base_subparser)
    _build_source_snapshot_freshness_subparser(source_subs, base_subparser)
    _build_run_operation_subparser(subs, base_subparser)

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