def main(args):
    """
    Perform analysis on the given logfiles and store the results in a machine-
    readable format.
    """
    logger.setup_logger(args.verbose if 'verbose' in args else None)

    # CTU loading mode is only meaningful if CTU itself is enabled.
    if 'ctu_ast_mode' in args and 'ctu_phases' not in args:
        LOG.error("Analyzer option 'ctu-ast-mode' requires CTU mode enabled")
        sys.exit(1)

    try:
        cmd_config.check_config_file(args)
    except FileNotFoundError as fnerr:
        LOG.error(fnerr)
        sys.exit(1)

    if not os.path.exists(args.logfile):
        LOG.error("The specified logfile '%s' does not exist!", args.logfile)
        sys.exit(1)

    args.output_path = os.path.abspath(args.output_path)
    if os.path.exists(args.output_path) and \
            not os.path.isdir(args.output_path):
        LOG.error("The given output path is not a directory: " +
                  args.output_path)
        sys.exit(1)

    if 'enable_all' in args:
        LOG.info("'--enable-all' was supplied for this analysis.")

    config_option_re = re.compile(r'^({}):.+=.+$'.format(
        '|'.join(analyzer_types.supported_analyzers)))

    # Check the format of analyzer options.
    if 'analyzer_config' in args:
        for config in args.analyzer_config:
            if not re.match(config_option_re, config):
                LOG.error("Analyzer option in wrong format: %s", config)
                sys.exit(1)

    # Check the format of checker options.
    if 'checker_config' in args:
        for config in args.checker_config:
            if not re.match(config_option_re, config):
                LOG.error("Checker option in wrong format: %s", config)
                sys.exit(1)

    # Process the skip list if present.
    skip_handler = __get_skip_handler(args)

    # Enable alpha uniqueing by default if ctu analysis is used.
    if 'none' in args.compile_uniqueing and 'ctu_phases' in args:
        args.compile_uniqueing = "alpha"

    compiler_info_file = None
    if 'compiler_info_file' in args:
        LOG.debug("Compiler info is read from: %s", args.compiler_info_file)
        if not os.path.exists(args.compiler_info_file):
            LOG.error("Compiler info file %s does not exist",
                      args.compiler_info_file)
            sys.exit(1)
        compiler_info_file = args.compiler_info_file

    ctu_or_stats_enabled = False
    # Skip list is applied only in pre-analysis
    # if --ctu-collect was called explicitly.
    pre_analysis_skip_handler = None
    if 'ctu_phases' in args:
        ctu_collect = args.ctu_phases[0]
        ctu_analyze = args.ctu_phases[1]
        if ctu_collect and not ctu_analyze:
            pre_analysis_skip_handler = skip_handler

        if ctu_collect or ctu_analyze:
            ctu_or_stats_enabled = True

    # Skip list is applied only in pre-analysis
    # if --stats-collect was called explicitly.
    if 'stats_output' in args and args.stats_output:
        pre_analysis_skip_handler = skip_handler
        ctu_or_stats_enabled = True

    if 'stats_enabled' in args and args.stats_enabled:
        ctu_or_stats_enabled = True

    context = analyzer_context.get_context()
    analyzer_env = env.extend(context.path_env_extra,
                              context.ld_lib_path_extra)

    compile_commands = load_json_or_empty(args.logfile)
    if compile_commands is None:
        sys.exit(1)

    # Number of all the compilation commands in the parsed log files,
    # logged by the logger.
    all_cmp_cmd_count = len(compile_commands)

    # We clear the output directory in the following cases.
    ctu_dir = os.path.join(args.output_path, 'ctu-dir')
    if 'ctu_phases' in args and args.ctu_phases[0] and \
            os.path.isdir(ctu_dir):
        # Clear the CTU-dir if the user turned on the collection phase.
        LOG.debug("Previous CTU contents have been deleted.")
        shutil.rmtree(ctu_dir)

    if 'clean' in args and os.path.isdir(args.output_path):
        LOG.info("Previous analysis results in '%s' have been removed, "
                 "overwriting with current result", args.output_path)
        shutil.rmtree(args.output_path)

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    plist_timestamps = {}
    for f in os.listdir(args.output_path):
        if not f.endswith('.plist'):
            continue
        plist_timestamps[f] = os.path.getmtime(
            os.path.join(args.output_path, f))

    # TODO: I'm not sure that this directory should be created here.
    fixit_dir = os.path.join(args.output_path, 'fixit')
    if not os.path.exists(fixit_dir):
        os.makedirs(fixit_dir)

    LOG.debug("args: %s", str(args))
    LOG.debug("Output will be stored to: '%s'", args.output_path)

    analyzer_clang_binary = \
        context.analyzer_binaries.get(
            clangsa.analyzer.ClangSA.ANALYZER_NAME)
    analyzer_clang_version = clangsa.version.get(analyzer_clang_binary,
                                                 analyzer_env)

    actions, skipped_cmp_cmd_count = log_parser.parse_unique_log(
        compile_commands,
        args.output_path,
        args.compile_uniqueing,
        compiler_info_file,
        args.keep_gcc_include_fixed,
        args.keep_gcc_intrin,
        skip_handler,
        pre_analysis_skip_handler,
        ctu_or_stats_enabled,
        analyzer_env,
        analyzer_clang_version)

    if not actions:
        LOG.info("No analysis is required.\nThere were no compilation "
                 "commands in the provided compilation database or "
                 "all of them were skipped.")
        sys.exit(0)

    uniqued_compilation_db_file = os.path.join(
        args.output_path, "unique_compile_commands.json")
    with open(uniqued_compilation_db_file, 'w',
              encoding="utf-8", errors="ignore") as f:
        json.dump(actions, f,
                  cls=log_parser.CompileCommandEncoder)

    metadata = {
        'version': 2,
        'tools': [{
            'name': 'codechecker',
            'action_num': len(actions),
            'command': sys.argv,
            'version': "{0} ({1})".format(context.package_git_tag,
                                          context.package_git_hash),
            'working_directory': os.getcwd(),
            'output_path': args.output_path,
            'result_source_files': {},
            'analyzers': {}
        }]}
    metadata_tool = metadata['tools'][0]

    if 'name' in args:
        metadata_tool['run_name'] = args.name

    # Update metadata dictionary with old values.
    metadata_file = os.path.join(args.output_path, 'metadata.json')
    metadata_prev = None
    if os.path.exists(metadata_file):
        metadata_prev = load_json_or_empty(metadata_file)
        metadata_tool['result_source_files'] = \
            __get_result_source_files(metadata_prev)

    CompileCmdParseCount = \
        collections.namedtuple('CompileCmdParseCount',
                               'total, analyze, skipped, removed_by_uniqueing')
    cmp_cmd_to_be_uniqued = all_cmp_cmd_count - skipped_cmp_cmd_count

    # Number of compile commands removed during uniqueing.
    removed_during_uniqueing = cmp_cmd_to_be_uniqued - len(actions)

    all_to_be_analyzed = cmp_cmd_to_be_uniqued - removed_during_uniqueing

    compile_cmd_count = CompileCmdParseCount(
        total=all_cmp_cmd_count,
        analyze=all_to_be_analyzed,
        skipped=skipped_cmp_cmd_count,
        removed_by_uniqueing=removed_during_uniqueing)

    LOG.debug_analyzer("Total number of compile commands without "
                       "skipping or uniqueing: %d", compile_cmd_count.total)
    LOG.debug_analyzer("Compile commands removed by uniqueing: %d",
                       compile_cmd_count.removed_by_uniqueing)
    LOG.debug_analyzer("Compile commands skipped during log processing: %d",
                       compile_cmd_count.skipped)
    LOG.debug_analyzer("Compile commands forwarded for analysis: %d",
                       compile_cmd_count.analyze)

    analyzer.perform_analysis(args, skip_handler, context, actions,
                              metadata_tool,
                              compile_cmd_count)

    __update_skip_file(args)
    __cleanup_metadata(metadata_prev, metadata)

    LOG.debug("Analysis metadata write to '%s'", metadata_file)
    with open(metadata_file, 'w',
              encoding="utf-8", errors="ignore") as metafile:
        json.dump(metadata, metafile)

    # WARN: store command will search for this file!!!!
    compile_cmd_json = os.path.join(args.output_path, 'compile_cmd.json')
    try:
        source = os.path.abspath(args.logfile)
        target = os.path.abspath(compile_cmd_json)

        if source != target:
            shutil.copyfile(source, target)
    except shutil.Error:
        LOG.debug("Compilation database JSON file is the same.")
    except Exception:
        LOG.debug("Copying compilation database JSON file failed.")

    try:
        # pylint: disable=no-name-in-module
        from codechecker_analyzer import analyzer_statistics
        analyzer_statistics.collect(metadata, "analyze")
    except Exception:
        pass

    # Generally exit status is set by sys.exit() call in CodeChecker. However,
    # exit codes 2 and 3 have a special meaning in case of an analysis:
    # 2 is returned in case of analyzer report emitted, 3 in case of analyzer
    # failed.
    # "CodeChecker analyze" is special in the sense that in can be invoked
    # either top-level or through "CodeChecker check". In the latter case
    # "CodeChecker check" should have the same exit status. Calling sys.exit()
    # at this specific point is not an option, because the remaining statements
    # of "CodeChecker check" after the analysis wouldn't execute.
    for analyzer_data in metadata_tool['analyzers'].values():
        if analyzer_data['analyzer_statistics']['failed'] != 0:
            return 3

    if __have_new_report(plist_timestamps, args.output_path):
        return 2