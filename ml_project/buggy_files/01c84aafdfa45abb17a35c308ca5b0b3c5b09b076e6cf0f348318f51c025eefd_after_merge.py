def start(filename=None, level=logging.INFO, to_console=True, to_file=True):
    """After initialization, start file logging.
    """
    global _logging_started

    assert _logging_configured
    if _logging_started:
        return

    # root logger
    logger = logging.getLogger()
    level = get_level_no(level)
    logger.setLevel(level)

    formatter = FlexGetFormatter()
    if to_file:
        file_handler = logging.handlers.RotatingFileHandler(filename, maxBytes=1000 * 1024, backupCount=9)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    # without --cron we log to console
    if to_console:
        # Make sure we don't send any characters that the current terminal doesn't support printing
        stdout = sys.stdout
        if hasattr(stdout, 'buffer'):
            # On python 3, we need to get the buffer directly to support writing bytes
            stdout = stdout.buffer
        safe_stdout = codecs.getwriter(io_encoding)(stdout, 'replace')
        console_handler = logging.StreamHandler(safe_stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    # flush what we have stored from the plugin initialization
    logger.removeHandler(_buff_handler)
    if _buff_handler:
        for record in _buff_handler.buffer:
            if logger.isEnabledFor(record.levelno):
                logger.handle(record)
        _buff_handler.flush()
    _logging_started = True