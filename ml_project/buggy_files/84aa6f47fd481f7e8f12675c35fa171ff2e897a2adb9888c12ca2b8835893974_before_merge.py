        def _do_lock(self):
            try:
                self._lock = zc.lockfile.LockFile(self.lockfile)
            except zc.lockfile.LockError:
                raise LockError(FAILED_TO_LOCK_MESSAGE)