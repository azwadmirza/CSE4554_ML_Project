def _setup_stdlib_logging(config, log_config, logBeginner: LogBeginner):
    """
    Set up Python stdlib logging.
    """
    if log_config is None:
        log_format = (
            "%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(request)s"
            " - %(message)s"
        )

        logger = logging.getLogger("")
        logger.setLevel(logging.INFO)
        logging.getLogger("synapse.storage.SQL").setLevel(logging.INFO)

        formatter = logging.Formatter(log_format)

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        logging.config.dictConfig(log_config)

    # We add a log record factory that runs all messages through the
    # LoggingContextFilter so that we get the context *at the time we log*
    # rather than when we write to a handler. This can be done in config using
    # filter options, but care must when using e.g. MemoryHandler to buffer
    # writes.

    log_filter = LoggingContextFilter(request="")
    old_factory = logging.getLogRecordFactory()

    def factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        log_filter.filter(record)
        return record

    logging.setLogRecordFactory(factory)

    # Route Twisted's native logging through to the standard library logging
    # system.
    observer = STDLibLogObserver()

    def _log(event):

        if "log_text" in event:
            if event["log_text"].startswith("DNSDatagramProtocol starting on "):
                return

            if event["log_text"].startswith("(UDP Port "):
                return

            if event["log_text"].startswith("Timing out client"):
                return

        return observer(event)

    logBeginner.beginLoggingTo([_log], redirectStandardIO=not config.no_redirect_stdio)
    if not config.no_redirect_stdio:
        print("Redirected stdout/stderr to logs")

    return observer