def isInThreadPool():
    """
    Check if we are currently on one of twisted threadpool threads.
    """
    threadpool = reactor.getThreadPool()
    return threadpool is not None and current_thread() in threadpool.threads