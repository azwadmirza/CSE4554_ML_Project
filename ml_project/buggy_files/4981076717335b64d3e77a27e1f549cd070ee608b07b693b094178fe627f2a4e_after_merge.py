        def rlimit(self, resource, limits=None):
            # if pid is 0 prlimit() applies to the calling process and
            # we don't want that
            if self.pid == 0:
                raise ValueError("can't use prlimit() against PID 0 process")
            try:
                if limits is None:
                    # get
                    return cext.linux_prlimit(self.pid, resource)
                else:
                    # set
                    if len(limits) != 2:
                        raise ValueError(
                            "second argument must be a (soft, hard) tuple")
                    soft, hard = limits
                    cext.linux_prlimit(self.pid, resource, soft, hard)
            except OSError as err:
                if err.errno == errno.ENOSYS and pid_exists(self.pid):
                    # I saw this happening on Travis:
                    # https://travis-ci.org/giampaolo/psutil/jobs/51368273
                    raise ZombieProcess(self.pid, self._name, self._ppid)
                else:
                    raise