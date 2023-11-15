    def acquire_write(self, timeout=_default_timeout):
        """Acquires a recursive, exclusive lock for writing.

        Read and write locks can be acquired and released in arbitrary
        order, but the POSIX lock is held until all local read and
        write locks are released.

        Returns True if it is the first acquire and actually acquires
        the POSIX lock, False if it is a nested transaction.

        """
        if self._writes == 0:
            self._lock(fcntl.LOCK_EX, timeout)   # can raise LockError.
            self._writes += 1
            return True
        else:
            self._writes += 1
            return False