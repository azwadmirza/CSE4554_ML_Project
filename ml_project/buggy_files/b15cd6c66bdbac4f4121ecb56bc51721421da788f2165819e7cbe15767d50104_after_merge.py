def backdown_thread_pool(max_workers=10):
    """Tries to create an executor with max_workers, but will back down ultimately to a single
    thread of the OS decides you can't have more than one.
    """
    from concurrent.futures import _base  # These "_" imports are gross, but I don't think there's an alternative  # NOQA
    from concurrent.futures.thread import _WorkItem

    class CondaThreadPoolExecutor(ThreadPoolExecutor):

        def submit(self, fn, *args, **kwargs):
            with self._shutdown_lock:
                if self._shutdown:
                    raise RuntimeError('cannot schedule new futures after shutdown')

                f = _base.Future()
                w = _WorkItem(f, fn, args, kwargs)

                self._work_queue.put(w)
                try:
                    self._adjust_thread_count()
                except RuntimeError:
                    # RuntimeError: can't start new thread
                    # See https://github.com/conda/conda/issues/6624
                    if len(self._threads) > 0:
                        # It's ok to not be able to start new threads if we already have at least
                        # one thread alive.
                        pass
                    else:
                        raise
                return f

    try:
        yield CondaThreadPoolExecutor(max_workers)
    except RuntimeError as e:  # pragma: no cover
        # RuntimeError is thrown if number of threads are limited by OS
        log.debug(repr(e))
        try:
            yield CondaThreadPoolExecutor(floor(max_workers / 2))
        except RuntimeError as e:
            log.debug(repr(e))
            yield CondaThreadPoolExecutor(1)