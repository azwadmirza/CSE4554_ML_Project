    def nice_get(self):
        # For some reason getpriority(3) return ESRCH (no such process)
        # for certain low-pid processes, no matter what (even as root).
        # The process actually exists though, as it has a name,
        # creation time, etc.
        # The best thing we can do here appears to be raising AD.
        # Note: tested on Solaris 11; on Open Solaris 5 everything is
        # fine.
        try:
            return cext_posix.getpriority(self.pid)
        except EnvironmentError as err:
            # 48 is 'operation not supported' but errno does not expose
            # it. It occurs for low system pids.
            if err.errno in (errno.ENOENT, errno.ESRCH, 48):
                if pid_exists(self.pid):
                    raise AccessDenied(self.pid, self._name)
            raise