    def pooled(*pargs, **kwargs):
        """
        A wrapper to run a thread in a thread pool
        """
        global running_async, async_lock
        result = func(*pargs, **kwargs)
        semaphore.release()
        with async_lock:
            running_async -= 1
        return result