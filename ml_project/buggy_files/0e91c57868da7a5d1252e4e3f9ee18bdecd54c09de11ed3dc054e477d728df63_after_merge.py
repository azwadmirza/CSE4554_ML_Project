    def _lock(self, op, timeout):
        """This takes a lock using POSIX locks (``fnctl.lockf``).

        The lock is implemented as a spin lock using a nonblocking
        call to lockf().

        On acquiring an exclusive lock, the lock writes this process's
        pid and host to the lock file, in case the holding process
        needs to be killed later.

        If the lock times out, it raises a ``LockError``.
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                # If this is already open read-only and we want to
                # upgrade to an exclusive write lock, close first.
                if self._fd is not None:
                    flags = fcntl.fcntl(self._fd, fcntl.F_GETFL)
                    if op == fcntl.LOCK_EX and flags | os.O_RDONLY:
                        os.close(self._fd)
                        self._fd = None

                if self._fd is None:
                    mode = os.O_RDWR if op == fcntl.LOCK_EX else os.O_RDONLY
                    self._fd = os.open(self._file_path, mode)

                fcntl.lockf(self._fd, op | fcntl.LOCK_NB)
                if op == fcntl.LOCK_EX:
                    os.write(
                        self._fd,
                        "pid=%s,host=%s" % (os.getpid(), socket.getfqdn()))
                return

            except IOError as error:
                if error.errno == errno.EAGAIN or error.errno == errno.EACCES:
                    pass
                else:
                    raise
            time.sleep(_sleep_time)

        raise LockError("Timed out waiting for lock.")