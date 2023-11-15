    def list_modules(self):
        modules = set()
        if self.options.module_path is not None:
            for i in self.options.module_path.split(os.pathsep):
                module_loader.add_directory(i)

        module_paths = module_loader._get_paths()
        for path in module_paths:
            if path is not None:
                modules.update(self._find_modules_in_path(path))
        return modules