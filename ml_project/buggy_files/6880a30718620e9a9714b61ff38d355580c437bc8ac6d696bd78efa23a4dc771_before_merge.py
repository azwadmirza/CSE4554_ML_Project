def shutdown_agents(opts):
    opts.connection.call('shutdown')
    _log.debug("Calling stop_platform")
    if opts.platform:
        opts.connection.notify('stop_platform')