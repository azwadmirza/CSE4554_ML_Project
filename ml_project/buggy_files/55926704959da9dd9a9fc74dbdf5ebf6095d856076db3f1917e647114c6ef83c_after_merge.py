    def load_class(self, conanfile_path):
        conanfile = self.cached_conanfiles.get(conanfile_path)
        if conanfile:
            return conanfile

        try:
            self._python_requires.valid = True
            _, conanfile = parse_conanfile(conanfile_path, self._python_requires)
            self._python_requires.valid = False
            self.cached_conanfiles[conanfile_path] = conanfile
            return conanfile
        except ConanException as e:
            raise ConanException("Error loading conanfile at '{}': {}".format(conanfile_path, e))