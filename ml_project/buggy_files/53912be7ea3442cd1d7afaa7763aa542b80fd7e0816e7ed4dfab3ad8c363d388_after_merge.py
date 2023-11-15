def shutdown_multiprocessing_logging_listener(daemonizing=False):
    global __MP_LOGGING_QUEUE
    global __MP_LOGGING_QUEUE_PROCESS
    global __MP_LOGGING_LISTENER_CONFIGURED

    if daemonizing is False and __MP_IN_MAINPROCESS is True:
        # We're in the MainProcess and we're not daemonizing, return!
        # No multiprocessing logging listener shutdown shall happen
        return

    if not daemonizing:
        # Need to remove the queue handler so that it doesn't try to send
        # data over a queue that was shut down on the listener end.
        shutdown_multiprocessing_logging()

    if __MP_LOGGING_QUEUE_PROCESS is None:
        return
    if __MP_LOGGING_QUEUE_PROCESS.is_alive():
        logging.getLogger(__name__).debug('Stopping the multiprocessing logging queue listener')
        try:
            # Sent None sentinel to stop the logging processing queue
            __MP_LOGGING_QUEUE.put(None)
            # Let's join the multiprocessing logging handle thread
            time.sleep(0.5)
            logging.getLogger(__name__).debug('closing multiprocessing queue')
            __MP_LOGGING_QUEUE.close()
            logging.getLogger(__name__).debug('joining multiprocessing queue thread')
            __MP_LOGGING_QUEUE.join_thread()
            __MP_LOGGING_QUEUE = None
            __MP_LOGGING_QUEUE_PROCESS.join(1)
            __MP_LOGGING_QUEUE = None
        except IOError:
            # We were unable to deliver the sentinel to the queue
            # carry on...
            pass
        if __MP_LOGGING_QUEUE_PROCESS.is_alive():
            # Process is still alive!?
            __MP_LOGGING_QUEUE_PROCESS.terminate()
        __MP_LOGGING_QUEUE_PROCESS = None
        __MP_LOGGING_LISTENER_CONFIGURED = False
        logging.getLogger(__name__).debug('Stopped the multiprocessing logging queue listener')