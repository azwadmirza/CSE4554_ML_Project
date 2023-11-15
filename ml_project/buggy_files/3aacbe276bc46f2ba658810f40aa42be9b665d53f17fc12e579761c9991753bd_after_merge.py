    def __init__(self):
        def u(v):
            return v.decode("utf-8") if isinstance(v, bytes) else v

        # qualifies the python
        self.platform = u(sys.platform)
        self.implementation = u(platform.python_implementation())
        if self.implementation == "PyPy":
            self.pypy_version_info = tuple(u(i) for i in sys.pypy_version_info)

        # this is a tuple in earlier, struct later, unify to our own named tuple
        self.version_info = VersionInfo(*list(u(i) for i in sys.version_info))
        self.architecture = 64 if sys.maxsize > 2 ** 32 else 32

        self.executable = u(sys.executable)  # executable we were called with
        self.original_executable = u(self.executable)
        self.base_executable = u(getattr(sys, "_base_executable", None))  # some platforms may set this

        self.version = u(sys.version)
        self.os = u(os.name)

        # information about the prefix - determines python home
        self.prefix = u(getattr(sys, "prefix", None))  # prefix we think
        self.base_prefix = u(getattr(sys, "base_prefix", None))  # venv
        self.real_prefix = u(getattr(sys, "real_prefix", None))  # old virtualenv

        # information about the exec prefix - dynamic stdlib modules
        self.base_exec_prefix = u(getattr(sys, "base_exec_prefix", None))
        self.exec_prefix = u(getattr(sys, "exec_prefix", None))

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
        config_var_keys = set()
        for element in self.sysconfig_paths.values():
            for k in _CONF_VAR_RE.findall(element):
                config_var_keys.add(u(k[1:-1]))
        self.sysconfig_config_vars = {u(i): u(sysconfig.get_config_var(i)) for i in config_var_keys}

        self.distutils_install = {u(k): u(v) for k, v in self._distutils_install().items()}