def is_ctu_capable(context):
    """ Detects if the current clang is CTU compatible. """
    enabled_analyzers, _ = \
        check_supported_analyzers([ClangSA.ANALYZER_NAME], context)
    if not enabled_analyzers:
        return False

    clangsa_cfg = ClangSA.construct_config_handler([], context)

    return clangsa_cfg.ctu_capability.is_ctu_capable