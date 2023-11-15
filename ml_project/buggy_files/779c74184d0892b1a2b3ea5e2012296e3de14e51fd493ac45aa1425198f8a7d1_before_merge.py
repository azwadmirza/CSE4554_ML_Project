    def kill(pid, signal):
        if not _is_pid_running(pid):
            raise OSError(errno.ESRCH, None)
        else:
            return