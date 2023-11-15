    def _raise_error():
        """
        Raises errors for inotify failures.
        """
        err = ctypes.get_errno()
        if err == errno.ENOSPC:
            raise OSError(errno.ENOSPC, "inotify watch limit reached")
        elif err == errno.EMFILE:
            raise OSError(errno.EMFILE, "inotify instance limit reached")
        elif err == errno.EACCES:
            # Prevent raising an exception when a file with no permissions
            # changes
            pass
        else:
            raise OSError(err, os.strerror(err))