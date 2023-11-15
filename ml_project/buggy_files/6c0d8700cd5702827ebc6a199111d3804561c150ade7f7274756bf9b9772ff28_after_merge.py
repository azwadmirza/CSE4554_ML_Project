def is_statistics_capable(context):
    """ Detects if the current clang is Statistics compatible. """
    # Resolve potentially missing binaries.
    enabled_analyzers, _ = \
        check_supported_analyzers([ClangSA.ANALYZER_NAME], context)
    if not enabled_analyzers:
        return False

    clangsa_cfg = ClangSA.construct_config_handler([], context)

    check_env = env.extend(context.path_env_extra,
                           context.ld_lib_path_extra)

    checkers = ClangSA.get_analyzer_checkers(clangsa_cfg, check_env)

    stat_checkers_pattern = re.compile(r'.+statisticscollector.+')

    for checker_name, _ in checkers:
        if stat_checkers_pattern.match(checker_name):
            return True

    return False