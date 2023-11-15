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