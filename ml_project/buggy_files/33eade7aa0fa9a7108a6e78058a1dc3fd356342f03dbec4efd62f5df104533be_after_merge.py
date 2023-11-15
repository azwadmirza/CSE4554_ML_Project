def init(config: dict) -> None:
    """
    Initializes this module with the given config,
    it does basic validation whether the specified
    exchange and pairs are valid.
    :param config: config to use
    :return: None
    """
    global _CONF, _API

    _CONF.update(config)

    if config['dry_run']:
        logger.info('Instance is running with dry_run enabled')

    exchange_config = config['exchange']
    _API = init_ccxt(exchange_config)

    logger.info('Using Exchange "%s"', get_name())

    # Check if all pairs are available
    validate_pairs(config['exchange']['pair_whitelist'])