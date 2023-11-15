def perform_analysis(args, skip_handler, context, actions, metadata_tool,
                     compile_cmd_count):
    """
    Perform static analysis via the given (or if not, all) analyzers,
    in the given analysis context for the supplied build actions.
    Additionally, insert statistical information into the metadata dict.
    """

    ctu_reanalyze_on_failure = 'ctu_reanalyze_on_failure' in args and \
        args.ctu_reanalyze_on_failure
    if ctu_reanalyze_on_failure:
        LOG.warning("Usage of a DEPRECATED FLAG!\n"
                    "The --ctu-reanalyze-on-failure flag will be removed "
                    "in the upcoming releases!")

    analyzers = args.analyzers if 'analyzers' in args \
        else analyzer_types.supported_analyzers
    analyzers, _ = analyzer_types.check_supported_analyzers(
        analyzers, context)

    ctu_collect = False
    ctu_analyze = False
    ctu_dir = ''
    if 'ctu_phases' in args:
        ctu_dir = os.path.join(args.output_path, 'ctu-dir')
        args.ctu_dir = ctu_dir
        if ClangSA.ANALYZER_NAME not in analyzers:
            LOG.error("CTU can only be used with the clang static analyzer.")
            return
        ctu_collect = args.ctu_phases[0]
        ctu_analyze = args.ctu_phases[1]

    if 'stats_enabled' in args and args.stats_enabled:
        if ClangSA.ANALYZER_NAME not in analyzers:
            LOG.debug("Statistics can only be used with "
                      "the Clang Static Analyzer.")
            return

    actions = prepare_actions(actions, analyzers)
    config_map = analyzer_types.build_config_handlers(args, context, analyzers)

    available_checkers = set()
    # Add profile names to the checkers list so we will not warn
    # if a profile is enabled but there is no checker with that name.
    available_checkers.update(context.profile_map.available_profiles())

    # Collect all the available checkers from the enabled analyzers.
    for analyzer in config_map.items():
        _, analyzer_cfg = analyzer
        for analyzer_checker in analyzer_cfg.checks().items():
            checker_name, _ = analyzer_checker
            available_checkers.add(checker_name)

    if 'ordered_checkers' in args:
        missing_checkers = checkers.available(args.ordered_checkers,
                                              available_checkers)
        if missing_checkers:
            LOG.warning("No checker(s) with these names was found:\n%s",
                        '\n'.join(missing_checkers))
            LOG.warning("Please review the checker names.\n"
                        "In the next release the analysis will not start "
                        "with invalid checker names.")

    if 'stats_enabled' in args:
        config_map[ClangSA.ANALYZER_NAME].set_checker_enabled(
            SpecialReturnValueCollector.checker_analyze)

        config_map[ClangSA.ANALYZER_NAME].set_checker_enabled(
            ReturnValueCollector.checker_analyze)

    # Statistics collector checkers must be explicitly disabled
    # as they trash the output.
    if "clangsa" in analyzers:
        config_map[ClangSA.ANALYZER_NAME].set_checker_enabled(
            SpecialReturnValueCollector.checker_collect, False)

        config_map[ClangSA.ANALYZER_NAME].set_checker_enabled(
            ReturnValueCollector.checker_collect, False)

    check_env = env.extend(context.path_env_extra,
                           context.ld_lib_path_extra)

    enabled_checkers = defaultdict(list)

    # Save some metadata information.
    for analyzer in analyzers:
        metadata_info = {
            'checkers': {},
            'analyzer_statistics': {
                "failed": 0,
                "failed_sources": [],
                "successful": 0,
                "version": None}}

        for check, data in config_map[analyzer].checks().items():
            state, _ = data
            metadata_info['checkers'].update({
                check: state == CheckerState.enabled})
            if state == CheckerState.enabled:
                enabled_checkers[analyzer].append(check)

        version = config_map[analyzer].get_version(check_env)
        metadata_info['analyzer_statistics']['version'] = version

        metadata_tool['analyzers'][analyzer] = metadata_info

    LOG.info("Enabled checkers:\n%s", '\n'.join(
        k + ': ' + ', '.join(v) for k, v in enabled_checkers.items()))

    if 'makefile' in args and args.makefile:
        statistics_data = __get_statistics_data(args)

        ctu_data = None
        if ctu_collect or statistics_data:
            ctu_data = __get_ctu_data(config_map, ctu_dir)

        makefile_creator = MakeFileCreator(analyzers, args.output_path,
                                           config_map, context, skip_handler,
                                           ctu_collect, statistics_data,
                                           ctu_data)
        makefile_creator.create(actions)
        return

    if ctu_collect:
        shutil.rmtree(ctu_dir, ignore_errors=True)
    elif ctu_analyze and not os.path.exists(ctu_dir):
        LOG.error("CTU directory: '%s' does not exist.", ctu_dir)
        return

    start_time = time.time()

    # Use Manager to create data objects which can be
    # safely shared between processes.
    manager = SyncManager()
    manager.start(__mgr_init)

    config_map = manager.dict(config_map)
    actions_map = create_actions_map(actions, manager)

    # Setting to not None value will enable statistical analysis features.
    statistics_data = __get_statistics_data(args)
    if statistics_data:
        statistics_data = manager.dict(statistics_data)

    if ctu_collect or statistics_data:
        ctu_data = None
        if ctu_collect or ctu_analyze:
            ctu_data = manager.dict(__get_ctu_data(config_map, ctu_dir))

        pre_analyze = [a for a in actions
                       if a.analyzer_type == ClangSA.ANALYZER_NAME]
        pre_anal_skip_handler = None

        # Skip list is applied only in pre-analysis
        # if --ctu-collect or --stats-collect  was called explicitly
        if ((ctu_collect and not ctu_analyze)
                or ("stats_output" in args and args.stats_output)):
            pre_anal_skip_handler = skip_handler

        clangsa_config = config_map.get(ClangSA.ANALYZER_NAME)

        if clangsa_config is not None:
            pre_analysis_manager.run_pre_analysis(pre_analyze,
                                                  context,
                                                  clangsa_config,
                                                  args.jobs,
                                                  pre_anal_skip_handler,
                                                  ctu_data,
                                                  statistics_data,
                                                  manager)
        else:
            LOG.error("Can not run pre analysis without clang "
                      "static analyzer configuration.")

    if 'stats_output' in args and args.stats_output:
        return

    if 'stats_dir' in args and args.stats_dir:
        statistics_data = manager.dict({'stats_out_dir': args.stats_dir})

    if ctu_analyze or statistics_data or (not ctu_analyze and not ctu_collect):

        LOG.info("Starting static analysis ...")
        analysis_manager.start_workers(actions_map, actions, context,
                                       config_map, args.jobs,
                                       args.output_path,
                                       skip_handler,
                                       metadata_tool,
                                       'quiet' in args,
                                       'capture_analysis_output' in args,
                                       args.timeout if 'timeout' in args
                                       else None,
                                       ctu_reanalyze_on_failure,
                                       statistics_data,
                                       manager,
                                       compile_cmd_count)
        LOG.info("Analysis finished.")
        LOG.info("To view results in the terminal use the "
                 "\"CodeChecker parse\" command.")
        LOG.info("To store results use the \"CodeChecker store\" command.")
        LOG.info("See --help and the user guide for further options about"
                 " parsing and storing the reports.")
        LOG.info("----=================----")

    end_time = time.time()
    LOG.info("Analysis length: %s sec.", end_time - start_time)

    metadata_tool['timestamps'] = {'begin': start_time,
                                   'end': end_time}

    if ctu_collect and ctu_analyze:
        shutil.rmtree(ctu_dir, ignore_errors=True)

    manager.shutdown()