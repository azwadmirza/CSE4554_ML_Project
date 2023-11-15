  def __init__(self, logger, log_level, handler):
    """
    :param logging.Logger logger: The logger instance to emit writes to.
    :param int log_level: The log level to use for the given logger.
    :param Handler handler: The underlying log handler, for determining the fileno
                            to support faulthandler logging.
    """
    self._logger = logger
    self._log_level = log_level
    self._handler = handler