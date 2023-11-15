    def load_class(self, conanfile_path):
        try:
            return self.cached_conanfiles[conanfile_path]
        except KeyError:
            self._python_requires.valid = True
            _, conanfile = parse_conanfile(conanfile_path, self._python_requires)
            self._python_requires.valid = False
            self.cached_conanfiles[conanfile_path] = conanfile
        return conanfile