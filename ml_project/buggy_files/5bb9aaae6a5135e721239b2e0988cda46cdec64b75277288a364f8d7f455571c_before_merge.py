  def __init__(self, logger, log_level, logger_stream):
    """
    :param logging.Logger logger: The logger instance to emit writes to.
    :param int log_level: The log level to use for the given logger.
    :param file logger_stream: The underlying file object the logger is writing to, for
                               determining the fileno to support faulthandler logging.
    """
    self._logger = logger
    self._log_level = log_level
    self._stream = logger_stream