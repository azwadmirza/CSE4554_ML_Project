    def create(self):
        dirs = self.ensure_directories()
        for directory in list(dirs):
            if any(i for i in dirs if i is not directory and directory.parts == i.parts[: len(directory.parts)]):
                dirs.remove(directory)
        for directory in sorted(dirs):
            ensure_dir(directory)

        self.set_pyenv_cfg()
        self.pyenv_cfg.write()
        true_system_site = self.enable_system_site_package
        try:
            self.enable_system_site_package = False
            for src in self._sources:
                src.run(self, self.symlinks)
        finally:
            if true_system_site != self.enable_system_site_package:
                self.enable_system_site_package = true_system_site
        super(ViaGlobalRefVirtualenvBuiltin, self).create()