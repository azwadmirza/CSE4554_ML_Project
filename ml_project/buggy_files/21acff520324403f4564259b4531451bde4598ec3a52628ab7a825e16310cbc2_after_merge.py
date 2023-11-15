    def __init__(self, argv, time, memory, nproc=1, executable=None, cwd=None, env=None,
                 network_block=False, inject32=None, inject64=None, inject_func=None):
        self.user = UserManager()
        self.process = ProcessManager(self.user.username, self.user.password)
        argv = list2cmdline(argv)
        if not isinstance(argv, unicode):
            argv = argv.decode('mbcs')
        self.process.command = argv
        if executable is not None:
            if not isinstance(executable, unicode):
                executable = executable.decode('mbcs')
            self.process.executable = executable
        if cwd is not None:
            self.process.dir = unicodify(cwd)
        if env is not None:
            self.process.set_environment(self._encode_environment(env))
        self.process.time_limit = time
        self.process.memory_limit = memory * 1024
        self.process.process_limit = nproc
        if inject32 is not None:
            self.process.inject32 = unicodify(inject32)
        if inject64 is not None:
            self.process.inject64 = unicodify(inject64)
        if inject_func is not None:
            self.process.inject_func = str(inject_func)
        self.returncode = None
        self.universal_newlines = False
        if executable is not None and network_block:
            # INetFwRules expects \, not / in paths, and fails with E_INVALIDARG if a path contains \
            # (even though this is valid in most other places in Windows)
            # See https://github.com/DMOJ/judge/issues/166 for more details
            executable.replace('/', '\\')
            self.network_block = NetworkManager('wbox_%s' % uuid1(), executable)
        else:
            self.network_block = None
        self.process.spawn()