    def _load(cls, path):
        """
        Returns a readable file-like object for the given path. If the path refers to a regular
        file, this method returns the result of invoking open() on the given path. If the path
        refers to a directory, this method returns a ZIP file with all files and subdirectories
        in the directory at the given path.

        :type path: str
        :rtype: io.FileIO
        """
        raise NotImplementedError()