    def __fspath__(self):
        """Comply with PathLike."""
        return os.fspath(self._file)