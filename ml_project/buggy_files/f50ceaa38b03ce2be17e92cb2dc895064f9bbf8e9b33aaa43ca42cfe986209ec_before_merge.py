def isInThreadPool():
    """
    Check if we are currently on one of twisted threadpool threads.
    """
    return bool(reactor.threadpool) and current_thread() in reactor.threadpool.threads