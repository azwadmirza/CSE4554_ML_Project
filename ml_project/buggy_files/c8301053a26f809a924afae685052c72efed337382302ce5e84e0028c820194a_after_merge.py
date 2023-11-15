def configure_file_logging(
    logger_obj: logging.Logger, log_file: Optional[Text]
) -> None:
    """Configure logging to a file.

    Args:
        logger_obj: Logger object to configure.
        log_file: Path of log file to write to.
    """
    if not log_file:
        return

    formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    file_handler = logging.FileHandler(log_file, encoding=io_utils.DEFAULT_ENCODING)
    file_handler.setLevel(logger_obj.level)
    file_handler.setFormatter(formatter)
    logger_obj.addHandler(file_handler)