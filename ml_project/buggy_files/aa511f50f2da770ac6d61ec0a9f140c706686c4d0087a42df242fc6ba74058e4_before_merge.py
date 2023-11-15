def check(check_data):
    """
    Invoke clang with an action which called by processes.
    Different analyzer object belongs to for each build action

    skiplist handler is None if no skip file was configured
    """
    args, action, context, analyzer_config_map, skp_handler, \
        report_output_dir, use_db = check_data

    try:
        # if one analysis fails the check fails
        return_codes = 0
        skipped = False
        for source in action.sources:

            # if there is no skiplist handler there was no skip list file
            # in the command line
            # cpp file skipping is handled here
            _, source_file_name = ntpath.split(source)

            if skp_handler and skp_handler.should_skip(source):
                LOG.debug_analyzer(source_file_name + ' is skipped')
                skipped = True
                continue

            # construct analyzer env
            analyzer_environment = analyzer_env.get_check_env(context.path_env_extra,
                                                      context.ld_lib_path_extra)
            run_id = context.run_id

            rh = analyzer_types.construct_result_handler(args,
                                                         action,
                                                         run_id,
                                                         report_output_dir,
                                                         context.severity_map,
                                                         skp_handler,
                                                         use_db)

            #LOG.info('Analysing ' + source_file_name)

            # create a source analyzer
            source_analyzer = analyzer_types.construct_analyzer(action,
                                                                analyzer_config_map)

            # source is the currently analyzed source file
            # there can be more in one buildaction
            source_analyzer.source_file = source

            # fills up the result handler with the analyzer information
            source_analyzer.analyze(rh, analyzer_environment)

            if rh.analyzer_returncode == 0:
                # analysis was successful
                # processing results
                if rh.analyzer_stdout != '':
                    LOG.debug_analyzer('\n' + rh.analyzer_stdout)
                if rh.analyzer_stderr != '':
                    LOG.debug_analyzer('\n' + rh.analyzer_stderr)
                rh.postprocess_result()
                rh.handle_results()
            else:
                # analisys failed
                LOG.error('Analyzing ' + source_file_name + ' failed.')
                if rh.analyzer_stdout != '':
                    LOG.error(rh.analyzer_stdout)
                if rh.analyzer_stderr != '':
                    LOG.error(rh.analyzer_stderr)
                return_codes = rh.analyzer_returncode

            if not args.keep_tmp:
                rh.clean_results()

        return (return_codes, skipped, action.analyzer_type)

    except Exception as e:
        LOG.debug_analyzer(str(e))
        traceback.print_exc(file=sys.stdout)
        return (1, action.analyzer_type)