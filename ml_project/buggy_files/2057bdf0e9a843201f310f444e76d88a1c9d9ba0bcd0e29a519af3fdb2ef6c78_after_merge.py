    def _lock(self, op, timeout=_default_timeout):
        """This takes a lock using POSIX locks (``fnctl.lockf``).

        The lock is implemented as a spin lock using a nonblocking call
        to lockf().

        On acquiring an exclusive lock, the lock writes this process's
        pid and host to the lock file, in case the holding process needs
        to be killed later.

        If the lock times out, it raises a ``LockError``.
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                # If we could write the file, we'd have opened it 'r+'.
                # Raise an error when we attempt to upgrade to a write lock.
                if op == fcntl.LOCK_EX:
                    if self._file and self._file.mode == 'r':
                        raise LockError(
                            "Can't take exclusive lock on read-only file: %s"
                            % self.path)

                # Create file and parent directories if they don't exist.
                if self._file is None:
                    self._ensure_parent_directory()

                    # Prefer to open 'r+' to allow upgrading to write
                    # lock later if possible.  Open read-only if we can't
                    # write the lock file at all.
                    os_mode, fd_mode = (os.O_RDWR | os.O_CREAT), 'r+'
                    if os.path.exists(self.path) and not os.access(
                            self.path, os.W_OK):
                        os_mode, fd_mode = os.O_RDONLY, 'r'

                    fd = os.open(self.path, os_mode)
                    self._file = os.fdopen(fd, fd_mode)

                # Try to get the lock (will raise if not available.)
                fcntl.lockf(self._file, op | fcntl.LOCK_NB,
                            self._length, self._start, os.SEEK_SET)

                # All locks read the owner PID and host
                self._read_lock_data()

                # Exclusive locks write their PID/host
                if op == fcntl.LOCK_EX:
                    self._write_lock_data()

                return

            except IOError as error:
                if error.errno == errno.EAGAIN or error.errno == errno.EACCES:
                    pass
                else:
                    raise
            time.sleep(_sleep_time)

        raise LockError("Timed out waiting for lock.")