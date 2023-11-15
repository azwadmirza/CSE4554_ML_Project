    def __init__(self):
        def u(v):
            return v.decode("utf-8") if isinstance(v, bytes) else v

        def abs_path(v):
            return None if v is None else os.path.abspath(v)  # unroll relative elements from path (e.g. ..)

        # qualifies the python
        self.platform = u(sys.platform)
        self.implementation = u(platform.python_implementation())
        if self.implementation == "PyPy":
            self.pypy_version_info = tuple(u(i) for i in sys.pypy_version_info)

        # this is a tuple in earlier, struct later, unify to our own named tuple
        self.version_info = VersionInfo(*list(u(i) for i in sys.version_info))
        self.architecture = 64 if sys.maxsize > 2 ** 32 else 32

        self.version = u(sys.version)
        self.os = u(os.name)

        # information about the prefix - determines python home
        self.prefix = u(abs_path(getattr(sys, "prefix", None)))  # prefix we think
        self.base_prefix = u(abs_path(getattr(sys, "base_prefix", None)))  # venv
        self.real_prefix = u(abs_path(getattr(sys, "real_prefix", None)))  # old virtualenv

        # information about the exec prefix - dynamic stdlib modules
        self.base_exec_prefix = u(abs_path(getattr(sys, "base_exec_prefix", None)))
        self.exec_prefix = u(abs_path(getattr(sys, "exec_prefix", None)))

        self.executable = u(abs_path(sys.executable))  # the executable we were invoked via
        self.original_executable = u(abs_path(self.executable))  # the executable as known by the interpreter
        self.system_executable = self._fast_get_system_executable()  # the executable we are based of (if available)

        try:
            __import__("venv")
            has = True
        except ImportError:
            has = False
        self.has_venv = has
        self.path = [u(i) for i in sys.path]
        self.file_system_encoding = u(sys.getfilesystemencoding())
        self.stdout_encoding = u(getattr(sys.stdout, "encoding", None))

        self.sysconfig_paths = {u(i): u(sysconfig.get_path(i, expand=False)) for i in sysconfig.get_path_names()}

        self.sysconfig = {
            u(k): u(v)
            for k, v in [  # a list of content to store from sysconfig
                ("makefile_filename", sysconfig.get_makefile_filename()),
            ]
            if k is not None
        }

        config_var_keys = set()
        for element in self.sysconfig_paths.values():
            for k in _CONF_VAR_RE.findall(element):
                config_var_keys.add(u(k[1:-1]))
        config_var_keys.add("PYTHONFRAMEWORK")

        self.sysconfig_vars = {u(i): u(sysconfig.get_config_var(i) or "") for i in config_var_keys}
        if self.implementation == "PyPy" and sys.version_info.major == 2:
            self.sysconfig_vars[u"implementation_lower"] = u"python"

        self.distutils_install = {u(k): u(v) for k, v in self._distutils_install().items()}
        confs = {k: (self.system_prefix if v.startswith(self.prefix) else v) for k, v in self.sysconfig_vars.items()}
        self.system_stdlib = self.sysconfig_path("stdlib", confs)
        self.system_stdlib_platform = self.sysconfig_path("platstdlib", confs)
        self.max_size = getattr(sys, "maxsize", getattr(sys, "maxint", None))
        self._creators = None