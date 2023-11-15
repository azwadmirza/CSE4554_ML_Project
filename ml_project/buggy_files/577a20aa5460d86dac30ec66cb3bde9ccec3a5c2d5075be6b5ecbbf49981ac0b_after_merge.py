    def __init__(self, options, interpreter):
        self.interpreter = interpreter
        self._debug = None
        self.dest_dir = Path(options.dest_dir)
        self.enable_system_site_package = options.system_site
        self.clear = options.clear
        self.pyenv_cfg = PyEnvCfg.from_folder(self.dest_dir)

        self._stdlib = None
        self._system_stdlib = None
        self._conf_vars = None