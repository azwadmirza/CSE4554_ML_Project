    def _resourcePath(self):
        """
        The path to the directory that should be used when shipping this module and its siblings
        around as a resource.
        """
        if '.' in self.name:
            return os.path.join(self.dirPath, self._rootPackage())
        else:
            initName = self._initModuleName(self.dirPath)
            if initName:
                raise ResourceException(
                    "Toil does not support loading a user script from a package directory. You "
                    "may want to remove %s from %s or invoke the user script as a module via "
                    "'PYTHONPATH=\"%s\" python -m %s.%s'." %
                    tuple(concat(initName, self.dirPath, os.path.split(self.dirPath), self.name)))
            return self.dirPath