def run_async(func):
    """
    Function decorator that will run the function in a new thread. A function
    decorated with this will have to include **kwargs in their parameter list,
    which will contain all optional parameters.

    Args:
        func (function): The function to run in the thread.

    Returns:
        function:
    """

    @wraps(func)
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

    @wraps(func)
    def async_func(*pargs, **kwargs):
        """
        A wrapper to run a function in a thread
        """
        global running_async, async_lock
        thread = Thread(target=pooled, args=pargs, kwargs=kwargs)
        semaphore.acquire()
        with async_lock:
            running_async += 1
        thread.start()
        return thread

    return async_func