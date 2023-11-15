    def _load(cls, leaderPath):
        """
        :type leaderPath: str
        """
        bytesIO = BytesIO()
        # PyZipFile compiles .py files on the fly, filters out any non-Python files and
        # distinguishes between packages and simple directories.
        with PyZipFile(file=bytesIO, mode='w') as zipFile:
            zipFile.writepy(leaderPath)
        bytesIO.seek(0)
        return bytesIO