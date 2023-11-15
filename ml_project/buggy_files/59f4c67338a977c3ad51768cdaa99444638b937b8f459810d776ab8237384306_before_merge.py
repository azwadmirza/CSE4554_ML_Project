def init(config: dict) -> None:
    """
    Initializes this module with the given config,
    registers all known command handlers
    and starts polling for message updates
    :param config: config to use
    :return: None
    """
    global _UPDATER

    _CONF.update(config)
    if not is_enabled():
        return

    _UPDATER = Updater(token=config['telegram']['token'], workers=0)

    # Register command handler and start telegram message polling
    handles = [
        CommandHandler('status', _status),
        CommandHandler('profit', _profit),
        CommandHandler('balance', _balance),
        CommandHandler('start', _start),
        CommandHandler('stop', _stop),
        CommandHandler('forcesell', _forcesell),
        CommandHandler('performance', _performance),
        CommandHandler('count', _count),
        CommandHandler('help', _help),
        CommandHandler('version', _version),
    ]
    for handle in handles:
        _UPDATER.dispatcher.add_handler(handle)
    _UPDATER.start_polling(
        clean=True,
        bootstrap_retries=3,
        timeout=30,
        read_latency=60,
    )
    logger.info(
        'rpc.telegram is listening for following commands: %s',
        [h.command for h in handles]
    )