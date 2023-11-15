    def env_paths(self):
        location = self.virtualenv_location if self.virtualenv_location else sys.prefix
        prefix = vistir.compat.Path(location)
        import importlib
        try:
            _virtualenv = importlib.import_module("virtualenv")
        except ImportError:
            with vistir.contextmanagers.temp_path():
                from string import Formatter
                formatter = Formatter()
                import sysconfig
                if getattr(sys, "real_prefix", None):
                    scheme = sysconfig._get_default_scheme()
                    sysconfig._INSTALL_SCHEMES["posix_prefix"]["purelib"]
                    if not scheme:
                        scheme = "posix_prefix" if not sys.platform == "win32" else "nt"
                    is_purelib = "purelib" in sysconfig._INSTALL_SCHEMES[scheme]
                    lib_key = "purelib" if is_purelib else "platlib"
                    lib = sysconfig._INSTALL_SCHEMES[scheme][lib_key]
                    fields = [field for _, field, _, _ in formatter.parse() if field]
                    config = {
                        "py_version_short": self._pyversion,
                    }
                    for field in fields:
                        if field not in config:
                            config[field] = prefix
                    sys.path = [
                        os.path.join(sysconfig._INSTALL_SCHEMES[scheme][lib_key], "site-packages"),
                    ] + sys.path
                    six.reload_module(importlib)
                    _virtualenv = importlib.import_module("virtualenv")
        home, lib, inc, bin_ = _virtualenv.path_locations(prefix.absolute().as_posix())
        paths = {
            "lib": lib,
            "include": inc,
            "scripts": bin_,
            "purelib": lib,
            "prefix": home,
            "base": home
        }
        return paths