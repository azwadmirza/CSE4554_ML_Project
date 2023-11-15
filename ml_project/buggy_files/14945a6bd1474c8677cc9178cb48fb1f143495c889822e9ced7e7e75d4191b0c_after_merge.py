def timeout(seconds=None, error_message="Timer expired"):
    """
    Timeout decorator to expire after a set number of seconds.  This raises an
    ansible.module_utils.facts.TimeoutError if the timeout is hit before the
    function completes.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            timeout_value = seconds
            if timeout_value is None:
                timeout_value = globals().get('GATHER_TIMEOUT') or DEFAULT_GATHER_TIMEOUT

            pool = mp.ThreadPool(processes=1)
            res = pool.apply_async(func, args, kwargs)
            pool.close()
            try:
                return res.get(timeout_value)
            except multiprocessing.TimeoutError:
                # This is an ansible.module_utils.common.facts.timeout.TimeoutError
                raise TimeoutError('Timer expired after %s seconds' % timeout_value)

        return wrapper

    # If we were called as @timeout, then the first parameter will be the
    # function we are to wrap instead of the number of seconds.  Detect this
    # and correct it by setting seconds to our default value and return the
    # inner decorator function manually wrapped around the function
    if callable(seconds):
        func = seconds
        seconds = None
        return decorator(func)

    # If we were called as @timeout([...]) then python itself will take
    # care of wrapping the inner decorator around the function

    return decorator