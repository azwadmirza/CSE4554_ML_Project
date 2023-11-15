    def _init(self, pid, _ignore_nsp=False):
        if pid is None:
            pid = os.getpid()
        else:
            if not _PY3 and not isinstance(pid, (int, long)):
                raise TypeError('pid must be an integer (got %r)' % pid)
            if pid < 0:
                raise ValueError('pid must be a positive integer (got %s)'
                                 % pid)
        self._pid = pid
        self._name = None
        self._exe = None
        self._create_time = None
        self._gone = False
        self._hash = None
        # used for caching on Windows only (on POSIX ppid may change)
        self._ppid = None
        # platform-specific modules define an _psplatform.Process
        # implementation class
        self._proc = _psplatform.Process(pid)
        self._last_sys_cpu_times = None
        self._last_proc_cpu_times = None
        # cache creation time for later use in is_running() method
        try:
            self.create_time()
        except AccessDenied:
            # we should never get here as AFAIK we're able to get
            # process creation time on all platforms even as a
            # limited user
            pass
        except ZombieProcess:
            # Let's consider a zombie process as legitimate as
            # tehcnically it's still alive (it can be queried,
            # although not always, and it's returned by pids()).
            pass
        except NoSuchProcess:
            if not _ignore_nsp:
                msg = 'no process found with pid %s' % pid
                raise NoSuchProcess(pid, None, msg)
            else:
                self._gone = True
        # This pair is supposed to indentify a Process instance
        # univocally over time (the PID alone is not enough as
        # it might refer to a process whose PID has been reused).
        # This will be used later in __eq__() and is_running().
        self._ident = (self.pid, self._create_time)