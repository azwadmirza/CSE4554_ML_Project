    def set_pyenv_cfg(self):
        self.pyenv_cfg.content = {
            "home": self.interpreter.system_exec_prefix,
            "include-system-site-packages": "true" if self.enable_system_site_package else "false",
            "implementation": self.interpreter.implementation,
            "virtualenv": __version__,
        }