    def _load_builtins(self):
        # Initialize declarations
        from . import builtins, arraydecl, npdatetime  # noqa: F401
        from . import ctypes_utils, bufproto           # noqa: F401

        self.install_registry(templates.builtin_registry)