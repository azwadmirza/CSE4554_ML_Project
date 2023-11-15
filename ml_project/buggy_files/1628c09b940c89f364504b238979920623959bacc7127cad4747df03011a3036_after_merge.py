    def acquire_read(self, timeout=_default_timeout):
        """Acquires a recursive, shared lock for reading.

        Read and write locks can be acquired and released in arbitrary
        order, but the POSIX lock is held until all local read and
        write locks are released.

        Returns True if it is the first acquire and actually acquires
        the POSIX lock, False if it is a nested transaction.

        """
        if self._reads == 0 and self._writes == 0:
            tty.debug('READ LOCK: {0.path}[{0._start}:{0._length}] [Acquiring]'
                      .format(self))
            self._lock(fcntl.LOCK_SH, timeout=timeout)   # can raise LockError.
            self._reads += 1
            return True
        else:
            self._reads += 1
            return False