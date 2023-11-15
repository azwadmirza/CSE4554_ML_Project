    def async_func(*args, **kwargs):
        """
        A wrapper to run a function in a thread
        """
        global running_async, async_lock
        thread = Thread(target=pooled, args=args, kwargs=kwargs)
        semaphore.acquire()
        with async_lock:
            running_async += 1
        thread.start()
        return thread