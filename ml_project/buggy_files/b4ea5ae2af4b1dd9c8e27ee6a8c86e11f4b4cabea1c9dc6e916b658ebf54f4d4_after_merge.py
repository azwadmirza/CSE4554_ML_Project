    def __str__(self):
        """Return the string version of the filename."""
        return os.fspath(self._file)