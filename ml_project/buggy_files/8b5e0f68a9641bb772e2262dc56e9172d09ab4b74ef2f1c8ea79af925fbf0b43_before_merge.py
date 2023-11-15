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
    finally:
        logging._releaseLock()