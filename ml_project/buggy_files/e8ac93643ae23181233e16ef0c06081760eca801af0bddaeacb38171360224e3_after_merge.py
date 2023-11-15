def get_logger(
        conf,
        name=None,
        verbose=False,
        fmt="%(process)d %(thread)X %(name)s %(levelname)s %(message)s"):
    if not conf:
        conf = {}
    if name is None:
        name = 'log'
    logger = logging.getLogger(name)
    logger.propagate = False

    syslog_prefix = conf.get('syslog_prefix', '')

    formatter = logging.Formatter(fmt=fmt)
    if syslog_prefix:
        fmt = '%s: %s' % (syslog_prefix, fmt)

    syslog_formatter = logging.Formatter(fmt=fmt)

    if not hasattr(get_logger, 'handler4logger'):
        get_logger.handler4logger = {}
    if logger in get_logger.handler4logger:
        logger.removeHandler(get_logger.handler4logger[logger])

    facility = getattr(SysLogHandler, conf.get('log_facility', 'LOG_LOCAL0'),
                       SysLogHandler.LOG_LOCAL0)

    log_address = conf.get('log_address', '/dev/log')
    try:
        handler = SysLogHandler(address=log_address, facility=facility)
    except socket.error as exc:
        if exc.errno not in [errno.ENOTSOCK, errno.ENOENT]:
            raise exc
        handler = SysLogHandler(facility=facility)

    handler.setFormatter(syslog_formatter)
    logger.addHandler(handler)
    get_logger.handler4logger[logger] = handler

    logging_level = getattr(logging,
                            conf.get('log_level', 'INFO').upper(),
                            logging.INFO)
    if (verbose or conf.get('is_cli') or
            hasattr(get_logger, 'console_handler4logger') or
            logging_level < logging.INFO):
        if not hasattr(get_logger, 'console_handler4logger'):
            get_logger.console_handler4logger = {}
        if logger in get_logger.console_handler4logger:
            logger.removeHandler(get_logger.console_handler4logger[logger])

        console_handler = logging.StreamHandler(sys.__stderr__)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        get_logger.console_handler4logger[logger] = console_handler

    logger.setLevel(logging_level)

    return logger