def shutdown_multiprocessing_logging():
    global __MP_LOGGING_CONFIGURED
    global __MP_LOGGING_QUEUE_HANDLER

    if not __MP_LOGGING_CONFIGURED or not __MP_LOGGING_QUEUE_HANDLER:
        return

    try:
        logging._acquireLock()
        # Let's remove the queue handler from the logging root handlers
        logging.root.removeHandler(__MP_LOGGING_QUEUE_HANDLER)
        __MP_LOGGING_QUEUE_HANDLER = None
        __MP_LOGGING_CONFIGURED = False
        if not logging.root.handlers:
            # Ensure we have at least one logging root handler so
            # something can handle logging messages. This case should
            # only occur on Windows since on Windows we log to console
            # and file through the Multiprocessing Logging Listener.
            setup_console_logger()
    finally:
        logging._releaseLock()