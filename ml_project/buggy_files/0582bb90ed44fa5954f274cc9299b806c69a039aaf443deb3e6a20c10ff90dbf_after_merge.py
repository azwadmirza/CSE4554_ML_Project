        def lock(self):
            try:
                super(Lock, self).lock(timedelta(seconds=DEFAULT_TIMEOUT))
            except flufl.lock.TimeOutError:
                raise LockError(FAILED_TO_LOCK_MESSAGE)