def _make_subtarget(targetctx, flags):
    """
    Make a new target context from the given target context and flags.
    """
    subtargetoptions = {}
    if flags.debuginfo:
        subtargetoptions['enable_debuginfo'] = True
    if flags.boundscheck:
        subtargetoptions['enable_boundscheck'] = True
    if flags.nrt:
        subtargetoptions['enable_nrt'] = True
    if flags.auto_parallel:
        subtargetoptions['auto_parallel'] = flags.auto_parallel
    if flags.fastmath:
        subtargetoptions['fastmath'] = flags.fastmath
    error_model = callconv.create_error_model(flags.error_model, targetctx)
    subtargetoptions['error_model'] = error_model

    return targetctx.subtarget(**subtargetoptions)