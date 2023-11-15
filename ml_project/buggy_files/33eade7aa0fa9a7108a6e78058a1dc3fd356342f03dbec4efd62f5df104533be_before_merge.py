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

    # Find matching class for the given exchange name
    name = exchange_config['name']

    if name not in ccxt.exchanges:
        raise OperationalException('Exchange {} is not supported'.format(name))
    try:
        _API = getattr(ccxt, name.lower())({
            'apiKey': exchange_config.get('key'),
            'secret': exchange_config.get('secret'),
            'password': exchange_config.get('password'),
            'uid': exchange_config.get('uid'),
            'enableRateLimit': True,
        })
    except (KeyError, AttributeError):
        raise OperationalException('Exchange {} is not supported'.format(name))

    logger.info('Using Exchange "%s"', get_name())

    # Check if all pairs are available
    validate_pairs(config['exchange']['pair_whitelist'])