def log(name: str, log_path: Union[str, bool] = intelmq.DEFAULT_LOGGING_PATH,
        log_level: str = intelmq.DEFAULT_LOGGING_LEVEL,
        stream: Optional[object] = None, syslog: Union[bool, str, list, tuple] = None,
        log_format_stream: str = LOG_FORMAT_STREAM,
        logging_level_stream: Optional[str] = None,
        log_max_size: Optional[int] = 0, log_max_copies: Optional[int] = None):
    """
    Returns a logger instance logging to file and sys.stderr or other stream.
    The warnings module will log to the same handlers.

    Parameters:
        name: filename for logfile or string preceding lines in stream
        log_path: Path to log directory, defaults to DEFAULT_LOGGING_PATH
            If False, nothing is logged to files.
        log_level: default is %r
        stream: By default (None), stdout and stderr will be used depending on the level.
            If False, stream output is not used.
            For everything else, the argument is used as stream output.
        syslog:
            If False (default), FileHandler will be used. Otherwise either a list/
            tuple with address and UDP port are expected, e.g. `["localhost", 514]`
            or a string with device name, e.g. `"/dev/log"`.
        log_format_stream:
            The log format used for streaming output. Default: LOG_FORMAT_STREAM
        logging_level_stream:
            The logging level for stream (console) output.
            By default the same as log_level.

    Returns:
        logger: An instance of logging.Logger

    See also:
        LOG_FORMAT: Default log format for file handler
        LOG_FORMAT_STREAM: Default log format for stream handler
        LOG_FORMAT_SYSLOG: Default log format for syslog
    """ % intelmq.DEFAULT_LOGGING_LEVEL
    logging.captureWarnings(True)
    warnings_logger = logging.getLogger("py.warnings")
    # set the name of the warnings logger to the bot neme, see #1184
    warnings_logger.name = name

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logging_level_stream:
        logging_level_stream = log_level

    if log_path and not syslog:
        handler = RotatingFileHandler("%s/%s.log" % (log_path, name),
                                      maxBytes=log_max_size,
                                      backupCount=log_max_copies)
        handler.setLevel(log_level)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
    elif syslog:
        if type(syslog) is tuple or type(syslog) is list:
            handler = logging.handlers.SysLogHandler(address=tuple(syslog))
        else:
            handler = logging.handlers.SysLogHandler(address=syslog)
        handler.setLevel(log_level)
        handler.setFormatter(logging.Formatter(LOG_FORMAT_SYSLOG))

    if log_path or syslog:
        logger.addHandler(handler)
        warnings_logger.addHandler(handler)

    if stream or stream is None:
        console_formatter = logging.Formatter(log_format_stream)
        if stream is None:
            console_handler = StreamHandler()
        else:
            console_handler = logging.StreamHandler(stream)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        warnings_logger.addHandler(console_handler)
        console_handler.setLevel(logging_level_stream)

    return logger