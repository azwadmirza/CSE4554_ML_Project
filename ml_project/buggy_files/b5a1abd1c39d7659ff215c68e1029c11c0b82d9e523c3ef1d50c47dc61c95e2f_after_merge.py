    def ppid(self):
        """The process parent PID.
        On Windows the return value is cached after first call.
        """
        # On POSIX we don't want to cache the ppid as it may unexpectedly
        # change to 1 (init) in case this process turns into a zombie:
        # https://github.com/giampaolo/psutil/issues/321
        # http://stackoverflow.com/questions/356722/

        # XXX should we check creation time here rather than in
        # Process.parent()?
        if _POSIX:
            ppid = self._proc.ppid()
        else:
            if self._ppid is None:
                ppid = self._proc.ppid()
            self._ppid = ppid
        self._proc._ppid = ppid
        return ppid