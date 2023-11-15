def _setup_emitter(general_config):
    emitter = general_config.emitter
    emitter.clear()
    emitter.banner(WORKLOCK_BANNER)
    return emitter