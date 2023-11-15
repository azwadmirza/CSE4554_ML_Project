def backdown_thread_pool(max_workers=10):
    """Tries to create an executor with max_workers, but will back down ultimately to a single
    thread of the OS decides you can't have more than one.
    """
    try:
        yield ThreadPoolExecutor(max_workers)
    except RuntimeError as e:  # pragma: no cover
        # RuntimeError is thrown if number of threads are limited by OS
        log.debug(repr(e))
        try:
            yield ThreadPoolExecutor(floor(max_workers / 2))
        except RuntimeError as e:
            log.debug(repr(e))
            yield ThreadPoolExecutor(1)