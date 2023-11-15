def is_z3_capable(context):
    """ Detects if the current clang is Z3 compatible. """
    enabled_analyzers, _ = \
        check_supported_analyzers([ClangSA.ANALYZER_NAME], context)
    if not enabled_analyzers:
        return False

    analyzer_binary = context.analyzer_binaries.get(ClangSA.ANALYZER_NAME)

    analyzer_env = env.extend(context.path_env_extra,
                              context.ld_lib_path_extra)

    return host_check.has_analyzer_option(analyzer_binary,
                                          ['-Xclang',
                                           '-analyzer-constraints=z3'],
                                          analyzer_env)