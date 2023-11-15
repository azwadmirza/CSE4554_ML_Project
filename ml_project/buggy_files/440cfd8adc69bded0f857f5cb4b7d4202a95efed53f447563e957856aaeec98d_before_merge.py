    def decorator(func):
        def _handle_timeout(signum, frame):
            msg = 'Timer expired after %s seconds' % globals().get('GATHER_TIMEOUT')
            raise TimeoutError(msg)

        def wrapper(*args, **kwargs):
            local_seconds = seconds
            if local_seconds is None:
                local_seconds = globals().get('GATHER_TIMEOUT') or DEFAULT_GATHER_TIMEOUT
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(local_seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper