    def _syscall_wrapper(func, recalc_timeout, *args, **kwargs):
        """ Wrapper function for syscalls that could fail due to EINTR.
        All functions should be retried if there is time left in the timeout
        in accordance with PEP 475. """
        timeout = kwargs.get("timeout", None)
        if timeout is None:
            expires = None
            recalc_timeout = False
        else:
            timeout = float(timeout)
            if timeout < 0.0:  # Timeout less than 0 treated as no timeout.
                expires = None
            else:
                expires = monotonic() + timeout

        args = list(args)
        if recalc_timeout and "timeout" not in kwargs:
            raise ValueError(
                "Timeout must be in args or kwargs to be recalculated")

        result = _SYSCALL_SENTINEL
        while result is _SYSCALL_SENTINEL:
            try:
                result = func(*args, **kwargs)
            # OSError is thrown by select.select
            # IOError is thrown by select.epoll.poll
            # select.error is thrown by select.poll.poll
            # Aren't we thankful for Python 3.x rework for exceptions?
            except (OSError, IOError, select.error) as e:
                # select.error wasn't a subclass of OSError in the past.
                errcode = None
                if hasattr(e, "errno"):
                    errcode = e.errno
                elif hasattr(e, "args"):
                    errcode = e.args[0]

                # Also test for the Windows equivalent of EINTR.
                is_interrupt = (errcode == errno.EINTR or (hasattr(errno, "WSAEINTR") and
                                                           errcode == errno.WSAEINTR))

                if is_interrupt:
                    if expires is not None:
                        current_time = monotonic()
                        if current_time > expires:
                            raise OSError(errno.ETIMEDOUT)
                        if recalc_timeout:
                            if "timeout" in kwargs:
                                kwargs["timeout"] = expires - current_time
                    continue
                if errcode:
                    raise SelectorError(errcode)
                else:
                    raise
        return result