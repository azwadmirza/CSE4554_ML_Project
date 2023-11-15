    def _resourcePath(self):
        """
        The path to the file or package directory that should be used when shipping this module
        around as a resource.
        """
        return self.dirPath if '.' in self.name else self.filePath