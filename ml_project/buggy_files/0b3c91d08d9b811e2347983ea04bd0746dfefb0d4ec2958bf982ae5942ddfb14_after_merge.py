    def load_class(self, conanfile_path):
        loaded, filename = parse_conanfile(conanfile_path)
        try:
            conanfile = _parse_module(loaded, filename)
            conanfile.python_requires = self._python_requires.requires
            return conanfile
        except Exception as e:  # re-raise with file name
            raise ConanException("%s: %s" % (conanfile_path, str(e)))