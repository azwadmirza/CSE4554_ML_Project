    def __init__(self, accountName, namePrefix, config=None, jobChunkSize=65535):
        self.jobChunkSize = jobChunkSize
        self.keyPath = None

        self.account_key = _fetchAzureAccountKey(accountName)

        # Table names have strict requirements in Azure
        self.namePrefix = self._sanitizeTableName(namePrefix)
        log.debug("Creating job store with name prefix '%s'" % self.namePrefix)

        # These are the main API entrypoints.
        self.tableService = TableService(account_key=self.account_key, account_name=accountName)
        self.blobService = BlobService(account_key=self.account_key, account_name=accountName)

        # Register our job-store in the global table for this storage account
        self.registryTable = self._getOrCreateTable('toilRegistry')
        exists = self.registryTable.get_entity(row_key=self.namePrefix)
        self._checkJobStoreCreation(config is not None, exists, accountName + ":" + self.namePrefix)
        self.registryTable.insert_or_replace_entity(row_key=self.namePrefix,
                                                    entity={'exists': True})

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