def configure_file_logging(logger_obj: logging.Logger, log_file: Optional[Text]):
    if not log_file:
        return

    formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    file_handler = logging.FileHandler(log_file, encoding=io_utils.DEFAULT_ENCODING)
    file_handler.setLevel(logger_obj.level)
    file_handler.setFormatter(formatter)
    logger_obj.addHandler(file_handler)