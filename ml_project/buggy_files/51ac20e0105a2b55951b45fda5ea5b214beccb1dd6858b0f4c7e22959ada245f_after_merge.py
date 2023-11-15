    def getJobStore(locator):
        """
        Create an instance of the concrete job store implementation that matches the given locator.

        :param str locator: The location of the job store to be represent by the instance

        :return: an instance of a concrete subclass of AbstractJobStore
        :rtype: toil.jobStores.abstractJobStore.AbstractJobStore
        """
        if locator[0] in '/.':
            locator = 'file:' + locator

        try:
            name, rest = locator.split(':', 1)
        except ValueError:
            raise RuntimeError('Invalid job store locator syntax.')

        if name == 'file':
            from toil.jobStores.fileJobStore import FileJobStore
            return FileJobStore(rest)

        elif name == 'aws':
            from toil.jobStores.aws.jobStore import AWSJobStore
            return AWSJobStore(rest)

        elif name == 'azure':
            from toil.jobStores.azureJobStore import AzureJobStore
            account, namePrefix = rest.split(':', 1)
            return AzureJobStore(account, namePrefix, config=config)
        
        elif name == 'google':
            from toil.jobStores.googleJobStore import GoogleJobStore
            projectID, namePrefix = rest.split(':', 1)
            return GoogleJobStore(namePrefix, projectID)
        else:
            raise RuntimeError("Unknown job store implementation '%s'" % name)