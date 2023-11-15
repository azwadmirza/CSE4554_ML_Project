    def __init__(self, accountName, namePrefix, config=None,
                 jobChunkSize=maxAzureTablePropertySize):
        self.jobChunkSize = jobChunkSize
        self.keyPath = None

        self.account_key = _fetchAzureAccountKey(accountName)
        self.accountName = accountName
        # Table names have strict requirements in Azure
        self.namePrefix = self._sanitizeTableName(namePrefix)
        logger.debug("Creating job store with name prefix '%s'" % self.namePrefix)

        # These are the main API entrypoints.
        self.tableService = TableService(account_key=self.account_key, account_name=accountName)
        self.blobService = BlobService(account_key=self.account_key, account_name=accountName)

        exists = self._jobStoreExists()
        self._checkJobStoreCreation(config is not None, exists, accountName + ":" + self.namePrefix)

        # Serialized jobs table
        self.jobItems = self._getOrCreateTable(self.qualify('jobs'))
        # Job<->file mapping table
        self.jobFileIDs = self._getOrCreateTable(self.qualify('jobFileIDs'))

        # Container for all shared and unshared files
        self.files = self._getOrCreateBlobContainer(self.qualify('files'))

        # Stats and logging strings
        self.statsFiles = self._getOrCreateBlobContainer(self.qualify('statsfiles'))
        # File IDs that contain stats and logging strings
        self.statsFileIDs = self._getOrCreateTable(self.qualify('statsFileIDs'))

        super(AzureJobStore, self).__init__(config=config)

        if self.config.cseKey is not None:
            self.keyPath = self.config.cseKey