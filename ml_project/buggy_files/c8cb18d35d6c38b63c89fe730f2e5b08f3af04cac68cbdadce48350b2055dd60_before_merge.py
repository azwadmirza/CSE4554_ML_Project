def main(args):
    """
    List the checkers available in the specified (or all supported) analyzers
    alongside with their description or enabled status in various formats.
    """

    # If the given output format is not 'table', redirect logger's output to
    # the stderr.
    logger.setup_logger(args.verbose if 'verbose' in args else None,
                        None if args.output_format == 'table' else 'stderr')

    context = analyzer_context.get_context()
    working_analyzers, errored = analyzer_types.check_supported_analyzers(
        args.analyzers,
        context)

    analyzer_environment = env.extend(context.path_env_extra,
                                      context.ld_lib_path_extra)

    analyzer_config_map = analyzer_types.build_config_handlers(
        args, context, working_analyzers)

    def uglify(text):
        """
        csv and json format output contain this non human readable header
        string: no CamelCase and no space.
        """
        return text.lower().replace(' ', '_')

    def match_guideline(checker_name, selected_guidelines):
        """
        Returns True if checker_name gives reports related to any of the
        selected guideline rule.
        checker_name -- A full checker name.
        selected_guidelines -- A list of guideline names or guideline rule IDs.
        """
        guideline = context.guideline_map.get(checker_name, {})
        guideline_set = set(guideline)
        for value in guideline.values():
            guideline_set |= set(value)

        return any(g in guideline_set for g in selected_guidelines)

    def format_guideline(guideline):
        """
        Convert guideline rules to human-readable format.
        guideline -- Dictionary in the following format:
                     {"guideline_1": ["rule_1", "rule_2"]}
        """
        return ' '.join('Related {} rules: {}'.format(g, ', '.join(r))
                        for g, r in guideline.items())

    # List available checker profiles.
    if 'profile' in args and args.profile == 'list':
        if 'details' in args:
            header = ['Profile name', 'Description']
            rows = context.profile_map.available_profiles().items()
        else:
            header = ['Profile name']
            rows = [(key, "") for key in
                    context.profile_map.available_profiles()]

        if args.output_format in ['csv', 'json']:
            header = list(map(uglify, header))

        print(twodim.to_str(args.output_format, header, rows))
        return

    # List checker config options.
    if 'checker_config' in args:
        if 'details' in args:
            header = ['Option', 'Description']
        else:
            header = ['Option']

        if args.output_format in ['csv', 'json']:
            header = list(map(uglify, header))

        rows = []
        for analyzer in working_analyzers:
            config_handler = analyzer_config_map.get(analyzer)
            analyzer_class = analyzer_types.supported_analyzers[analyzer]

            configs = analyzer_class.get_checker_config(config_handler,
                                                        analyzer_environment)
            rows.extend((':'.join((analyzer, c[0])), c[1]) if 'details' in args
                        else (':'.join((analyzer, c[0])),) for c in configs)

        print(twodim.to_str(args.output_format, header, rows))
        return

    if args.guideline is not None and len(args.guideline) == 0:
        result = defaultdict(set)

        for _, guidelines in context.guideline_map.items():
            for guideline, rules in guidelines.items():
                result[guideline] |= set(rules)

        header = ['Guideline', 'Rules']
        if args.output_format in ['csv', 'json']:
            header = list(map(uglify, header))

        if args.output_format == 'json':
            rows = [(g, sorted(list(r))) for g, r in result.items()]
        else:
            rows = [(g, ', '.join(sorted(r))) for g, r in result.items()]

        if args.output_format == 'rows':
            for row in rows:
                print('Guideline: {}'.format(row[0]))
                print('Rules: {}'.format(row[1]))
        else:
            print(twodim.to_str(args.output_format, header, rows))
        return

    # List available checkers.
    if 'details' in args:
        header = ['Enabled', 'Name', 'Analyzer', 'Severity', 'Guideline',
                  'Description']
    else:
        header = ['Name']

    if args.output_format in ['csv', 'json']:
        header = list(map(uglify, header))

    rows = []
    for analyzer in working_analyzers:
        config_handler = analyzer_config_map.get(analyzer)
        analyzer_class = analyzer_types.supported_analyzers[analyzer]

        checkers = analyzer_class.get_analyzer_checkers(config_handler,
                                                        analyzer_environment)

        profile_checkers = []
        if 'profile' in args:
            if args.profile not in context.profile_map.available_profiles():
                LOG.error("Checker profile '%s' does not exist!",
                          args.profile)
                LOG.error("To list available profiles, use '--profile list'.")
                sys.exit(1)

            profile_checkers = [('profile:' + args.profile, True)]

        config_handler.initialize_checkers(context,
                                           checkers,
                                           profile_checkers)

        for checker_name, value in config_handler.checks().items():
            state, description = value

            if state != CheckerState.enabled and 'profile' in args:
                continue

            if state == CheckerState.enabled and 'only_disabled' in args:
                continue
            elif state != CheckerState.enabled and 'only_enabled' in args:
                continue

            if args.output_format == 'json':
                state = state == CheckerState.enabled
            else:
                state = '+' if state == CheckerState.enabled else '-'

            if args.guideline is not None:
                if not match_guideline(checker_name, args.guideline):
                    continue

            if 'details' in args:
                severity = context.severity_map.get(checker_name)
                guideline = context.guideline_map.get(checker_name, {})
                if args.output_format != 'json':
                    guideline = format_guideline(guideline)
                rows.append([state, checker_name, analyzer,
                             severity, guideline, description])
            else:
                rows.append([checker_name])

    if 'show_warnings' in args:
        severity = context.severity_map.get('clang-diagnostic-')
        for warning in get_warnings(analyzer_environment):
            warning = 'clang-diagnostic-' + warning

            if args.guideline is not None:
                if not match_guideline(warning, args.guideline):
                    continue

            guideline = context.guideline_map.get(warning, {})
            if args.output_format != 'json':
                guideline = format_guideline(guideline)

            if 'details' in args:
                rows.append(['', warning, '-', severity, guideline, '-'])
            else:
                rows.append([warning])

    if rows:
        print(twodim.to_str(args.output_format, header, rows))

    for analyzer_binary, reason in errored:
        LOG.error("Failed to get checkers for '%s'!"
                  "The error reason was: '%s'", analyzer_binary, reason)
        LOG.error("Please check your installation and the "
                  "'config/package_layout.json' file!")