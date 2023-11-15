    def __init__(self):
        # qualifies the python
        self.platform = sys.platform
        self.implementation = platform.python_implementation()
        self.pypy_version_info = tuple(sys.pypy_version_info) if self.implementation == "PyPy" else None

        # this is a tuple in earlier, struct later, unify to our own named tuple
        self.version_info = VersionInfo(*list(sys.version_info))
        self.architecture = 64 if sys.maxsize > 2 ** 32 else 32

        self.executable = sys.executable  # executable we were called with
        self.original_executable = self.executable
        self.base_executable = getattr(sys, "_base_executable", None)  # some platforms may set this

        self.version = sys.version
        self.os = os.name

        # information about the prefix - determines python home
        self.prefix = getattr(sys, "prefix", None)  # prefix we think
        self.base_prefix = getattr(sys, "base_prefix", None)  # venv
        self.real_prefix = getattr(sys, "real_prefix", None)  # old virtualenv

        # information about the exec prefix - dynamic stdlib modules
        self.base_exec_prefix = getattr(sys, "base_exec_prefix", None)
        self.exec_prefix = getattr(sys, "exec_prefix", None)

        try:
            __import__("venv")
            has = True
        except ImportError:
            has = False
        self.has_venv = has
        self.path = sys.path
        self.file_system_encoding = sys.getfilesystemencoding()
        self.stdout_encoding = getattr(sys.stdout, "encoding", None)