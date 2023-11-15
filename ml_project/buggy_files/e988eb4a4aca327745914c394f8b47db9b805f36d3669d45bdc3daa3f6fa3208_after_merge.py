    def __init__(self, name: str, project: str, suite: str, fname: T.List[str],
                 is_cross_built: bool, exe_wrapper: T.Optional[dependencies.ExternalProgram],
                 needs_exe_wrapper: bool, is_parallel: bool, cmd_args: T.List[str],
                 env: build.EnvironmentVariables, should_fail: bool,
                 timeout: T.Optional[int], workdir: T.Optional[str],
                 extra_paths: T.List[str], protocol: TestProtocol, priority: int,
                 cmd_is_built: bool, depends: T.List[str], version: str):
        self.name = name
        self.project_name = project
        self.suite = suite
        self.fname = fname
        self.is_cross_built = is_cross_built
        if exe_wrapper is not None:
            assert(isinstance(exe_wrapper, dependencies.ExternalProgram))
        self.exe_runner = exe_wrapper
        self.is_parallel = is_parallel
        self.cmd_args = cmd_args
        self.env = env
        self.should_fail = should_fail
        self.timeout = timeout
        self.workdir = workdir
        self.extra_paths = extra_paths
        self.protocol = protocol
        self.priority = priority
        self.needs_exe_wrapper = needs_exe_wrapper
        self.cmd_is_built = cmd_is_built
        self.depends = depends
        self.version = version