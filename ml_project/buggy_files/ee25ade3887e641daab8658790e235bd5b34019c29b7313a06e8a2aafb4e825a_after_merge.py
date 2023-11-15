    def __init__(self, locator, jobChunkSize=maxAzureTablePropertySize):
        super(AzureJobStore, self).__init__()
        accountName, namePrefix = locator.split(':', 1)
        if '--' in namePrefix:
            raise ValueError("Invalid name prefix '%s'. Name prefixes may not contain %s."
                             % (namePrefix, self.nameSeparator))
        if not self.containerNameRe.match(namePrefix):
            raise ValueError("Invalid name prefix '%s'. Name prefixes must contain only digits, "
                             "hyphens or lower-case letters and must not start or end in a "
                             "hyphen." % namePrefix)
        # Reserve 13 for separator and suffix
        if len(namePrefix) > self.maxContainerNameLen - self.maxNameLen - len(self.nameSeparator):
            raise ValueError(("Invalid name prefix '%s'. Name prefixes may not be longer than 50 "
                              "characters." % namePrefix))
        if '--' in namePrefix:
            raise ValueError("Invalid name prefix '%s'. Name prefixes may not contain "
                             "%s." % (namePrefix, self.nameSeparator))
        self.locator = locator
        self.jobChunkSize = jobChunkSize
        self.accountKey = _fetchAzureAccountKey(accountName)
        self.accountName = accountName
        # Table names have strict requirements in Azure
        self.namePrefix = self._sanitizeTableName(namePrefix)
        # These are the main API entry points.
        self.tableService = TableService(account_key=self.accountKey, account_name=accountName)
        self.blobService = BlobService(account_key=self.accountKey, account_name=accountName)
        # Serialized jobs table
        self.jobItems = None
        # Job<->file mapping table
        self.jobFileIDs = None
        # Container for all shared and unshared files
        self.files = None
        # Stats and logging strings
        self.statsFiles = None
        # File IDs that contain stats and logging strings
        self.statsFileIDs = None