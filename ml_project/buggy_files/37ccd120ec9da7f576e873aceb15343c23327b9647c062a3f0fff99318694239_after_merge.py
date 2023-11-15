    def __init__(self, path):
        """
        :param str path: Path to directory holding the job store
        """
        super(FileJobStore, self).__init__()
        self.jobStoreDir = absSymPath(path)
        logger.info("Path to job store directory is '%s'.", self.jobStoreDir)
        # Directory where temporary files go
        self.tempFilesDir = os.path.join(self.jobStoreDir, 'tmp')