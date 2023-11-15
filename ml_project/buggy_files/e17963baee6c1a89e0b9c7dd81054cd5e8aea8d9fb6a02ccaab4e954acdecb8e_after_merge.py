def main():
    """
    Loads and validates the config and handles the main loop
    :return: None
    """
    global _CONF
    args = build_arg_parser().parse_args()

    # Initialize logger
    logging.basicConfig(
        level=args.loglevel,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    logger.info(
        'Starting freqtrade %s (loglevel=%s)',
        __version__,
        logging.getLevelName(args.loglevel)
    )

    # Load and validate configuration
    with open(args.config) as file:
        _CONF = json.load(file)
    if 'internals' not in _CONF:
        _CONF['internals'] = {}
    logger.info('Validating configuration ...')
    validate(_CONF, CONF_SCHEMA)

    # Initialize all modules and start main loop
    if args.dynamic_whitelist:
        logger.info('Using dynamically generated whitelist. (--dynamic-whitelist detected)')
    init(_CONF)
    old_state = None
    while True:
        new_state = get_state()
        # Log state transition
        if new_state != old_state:
            telegram.send_msg('*Status:* `{}`'.format(new_state.name.lower()))
            logger.info('Changing state to: %s', new_state.name)

        if new_state == State.STOPPED:
            time.sleep(1)
        elif new_state == State.RUNNING:
            throttle(
                _process,
                min_secs=_CONF['internals'].get('process_throttle_secs', 10),
                dynamic_whitelist=args.dynamic_whitelist,
            )
        old_state = new_state