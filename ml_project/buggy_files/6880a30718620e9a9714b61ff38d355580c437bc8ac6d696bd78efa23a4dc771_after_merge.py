def shutdown_agents(opts):
    if 'rmq' == utils.get_messagebus() and not check_rabbit_status():
        opts.aip.rmq_shutdown()
    else:
        opts.connection.call('shutdown')
        _log.debug("Calling stop_platform")
        if opts.platform:
            opts.connection.notify('stop_platform')