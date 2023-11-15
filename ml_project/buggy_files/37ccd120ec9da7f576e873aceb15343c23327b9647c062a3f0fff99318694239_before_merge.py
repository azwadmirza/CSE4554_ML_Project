    def __init__(self, jobStoreDir, config=None):
        """
        :param jobStoreDir: Place to create jobStore
        :param config: See jobStores.abstractJobStore.AbstractJobStore.__init__
        :raise RuntimeError: if config != None and the jobStore already exists or
        config == None and the jobStore does not already exists. 
        """
        # This is root directory in which everything in the store is kept
        self.jobStoreDir = absSymPath(jobStoreDir)
        logger.info("Jobstore directory is: %s", self.jobStoreDir)
        # Safety checks for existing jobStore
        self._checkJobStoreCreation(create=config is not None,
                                    exists=os.path.exists(self.jobStoreDir),
                                    locator=self.jobStoreDir)
        # Directory where temporary files go
        self.tempFilesDir = os.path.join(self.jobStoreDir, "tmp")
        # Creation of jobStore, if necessary
        if config is not None:
            os.mkdir(self.jobStoreDir)
            os.mkdir(self.tempFilesDir)
        # Parameters for creating temporary files
        self.validDirs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        self.levels = 2
        super(FileJobStore, self).__init__(config=config)